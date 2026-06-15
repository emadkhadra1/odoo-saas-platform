from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaasSubscription(models.Model):
    """Billing contract between a tenant and a SaaS plan."""

    _name = "saas.subscription"
    _description = "SaaS Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_billing_date asc, create_date desc"

    tenant_id = fields.Many2one("saas.tenant", required=True, ondelete="cascade", tracking=True)
    plan_id = fields.Many2one("saas.plan", required=True, tracking=True)
    billing_cycle = fields.Selection([("monthly", "Monthly"), ("yearly", "Yearly")], default="monthly", required=True, tracking=True)
    amount = fields.Monetary(required=True, tracking=True)
    currency_id = fields.Many2one(related="plan_id.currency_id", store=True, readonly=True)
    start_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    end_date = fields.Date(tracking=True)
    next_billing_date = fields.Date(tracking=True)
    payment_status = fields.Selection(
        [("unpaid", "Unpaid"), ("paid", "Paid"), ("failed", "Failed"), ("refunded", "Refunded")],
        default="unpaid",
        required=True,
        tracking=True,
    )
    subscription_status = fields.Selection(
        [("trial", "Trial"), ("active", "Active"), ("suspended", "Suspended"), ("cancelled", "Cancelled"), ("expired", "Expired")],
        default="trial",
        required=True,
        tracking=True,
    )
    auto_renew = fields.Boolean(default=True)
    invoice_ids = fields.Many2many("account.move", string="Invoices", domain=[("move_type", "=", "out_invoice")])
    payment_ids = fields.One2many("saas.payment", "subscription_id")

    @api.onchange("plan_id", "billing_cycle")
    def _onchange_amount(self):
        for subscription in self:
            if subscription.plan_id:
                subscription.amount = (
                    subscription.plan_id.yearly_price
                    if subscription.billing_cycle == "yearly"
                    else subscription.plan_id.monthly_price
                )

    @api.onchange("start_date", "billing_cycle")
    def _onchange_next_billing_date(self):
        for subscription in self:
            subscription.next_billing_date = subscription._get_next_billing_date()

    def _get_next_billing_date(self):
        self.ensure_one()
        if not self.start_date:
            return False
        months = 12 if self.billing_cycle == "yearly" else 1
        return self.start_date + relativedelta(months=months)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            plan = self.env["saas.plan"].browse(vals.get("plan_id")) if vals.get("plan_id") else False
            if plan and not vals.get("amount"):
                vals["amount"] = plan.yearly_price if vals.get("billing_cycle") == "yearly" else plan.monthly_price
            if not vals.get("next_billing_date") and vals.get("start_date"):
                start_date = fields.Date.to_date(vals["start_date"])
                months = 12 if vals.get("billing_cycle") == "yearly" else 1
                vals["next_billing_date"] = start_date + relativedelta(months=months)
        records = super().create(vals_list)
        for record in records:
            if not record.tenant_id.subscription_id:
                record.tenant_id.subscription_id = record
        return records

    def action_suspend(self):
        for subscription in self:
            subscription.write({"subscription_status": "suspended", "payment_status": "failed"})
            subscription.tenant_id.action_suspend()
        return True

    def action_reactivate(self):
        for subscription in self:
            subscription.write({"subscription_status": "active", "payment_status": "paid"})
            subscription.tenant_id.action_reactivate()
        return True

    def _cron_check_subscriptions(self):
        today = fields.Date.context_today(self)
        subscriptions = self.search([("subscription_status", "in", ("trial", "active")), ("auto_renew", "=", True)])
        for subscription in subscriptions:
            if subscription.subscription_status == "trial" and subscription.end_date and subscription.end_date < today:
                subscription.write({"subscription_status": "suspended", "payment_status": "unpaid"})
                subscription.tenant_id.action_suspend()
                continue
            if subscription.next_billing_date and subscription.next_billing_date <= today:
                invoice = subscription._create_invoice_if_available()
                next_date = subscription.next_billing_date + relativedelta(months=12 if subscription.billing_cycle == "yearly" else 1)
                vals = {"next_billing_date": next_date, "payment_status": "unpaid"}
                if invoice:
                    vals["invoice_ids"] = [(4, invoice.id)]
                subscription.write(vals)
                subscription.tenant_id.write({"next_invoice_date": next_date})
        expired = self.search([("end_date", "!=", False), ("end_date", "<", today), ("subscription_status", "not in", ("cancelled", "expired"))])
        for subscription in expired:
            subscription.write({"subscription_status": "expired"})
            subscription.tenant_id.write({"status": "expired", "expiry_date": subscription.end_date})

    def _create_invoice_if_available(self):
        self.ensure_one()
        if "account.move" not in self.env:
            return False
        partner = self.tenant_id._get_or_create_billing_partner()
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_origin": self.tenant_id.name,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "%s SaaS subscription - %s" % (self.plan_id.name, self.billing_cycle),
                            "quantity": 1,
                            "price_unit": self.amount,
                        },
                    )
                ],
            }
        )
        return invoice
