from odoo import fields, models


class SaasPayment(models.Model):
    """Manual or gateway-originated tenant payment record."""

    _name = "saas.payment"
    _description = "SaaS Payment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "payment_date desc, create_date desc"

    tenant_id = fields.Many2one("saas.tenant", required=True, ondelete="cascade", tracking=True)
    subscription_id = fields.Many2one("saas.subscription", required=True, ondelete="cascade", tracking=True)
    amount = fields.Monetary(required=True, tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, required=True)
    payment_date = fields.Date(default=fields.Date.context_today, tracking=True)
    payment_method = fields.Char(tracking=True)
    transaction_reference = fields.Char(copy=False, tracking=True)
    status = fields.Selection(
        [("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("cancelled", "Cancelled")],
        default="pending",
        required=True,
        tracking=True,
    )
    notes = fields.Text()

    def action_mark_paid(self):
        for payment in self:
            payment.write({"status": "paid"})
            payment.subscription_id.write({"payment_status": "paid", "subscription_status": "active"})
            payment.tenant_id.write({"last_payment_date": payment.payment_date, "status": "active"})

    def action_mark_failed(self):
        self.write({"status": "failed"})
