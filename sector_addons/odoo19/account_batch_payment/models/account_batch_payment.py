from odoo import _, fields, models


class AccountBatchPayment(models.Model):
    _name = "account.batch.payment"
    _description = "Batch Payment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default=lambda self: _("New"), copy=False, tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    batch_type = fields.Selection(
        [("inbound", "Receive"), ("outbound", "Send")],
        default="outbound",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("post", "Posted"), ("sent", "Sent"), ("reconciled", "Reconciled")],
        default="draft",
        copy=False,
        tracking=True,
    )
    journal_id = fields.Many2one("account.journal", required=True)
    payment_method_id = fields.Many2one("account.payment.method")
    payment_ids = fields.One2many("account.payment", "batch_payment_id", string="Payments")
    file_generation_enabled = fields.Boolean(default=False)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    def action_post_payment(self):
        for batch in self:
            for payment in batch.payment_ids.filtered(lambda item: item.state == "draft"):
                payment.action_post()
            batch.state = "post"

    def validate_batch(self):
        self.write({"state": "sent"})

    def export_batch_payment(self):
        return True

    def print_batch_payment(self):
        return True


class AccountPayment(models.Model):
    _inherit = "account.payment"

    batch_payment_id = fields.Many2one("account.batch.payment", string="Batch Payment")
    batch_name = fields.Char("Batch Transfer Name")
    ref = fields.Char(string="Reference")
    payment_date = fields.Date(string="Payment Date")
    due_date = fields.Date(string="Due Date")
    invoice_date_due = fields.Date(string="Invoice Due Date")
    communication = fields.Char(string="Communication")
    payment_method_id = fields.Many2one("account.payment.method", string="Payment Method")
    payment_type_check = fields.Selection(
        [("payment", "Payment"), ("check", "Cheque")],
        default="payment",
        string="Payment Method Type",
    )
    partner_bank = fields.Many2one("res.bank", string="Partner Bank")
    check_no = fields.Char("Check No.")
    so_id = fields.Many2one("sale.order", string="Sale Order")
    install_id = fields.Many2one("account.move", string="Installment")
    analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic Account")
    other_destination_account_id = fields.Many2one("account.account", string="Destination Account")
