from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    custody_id = fields.Many2one(comodel_name='financial.custody', string='Custody')
    is_custody_payment = fields.Boolean(default=False)
    custody_remaining_amount = fields.Float()

    @api.constrains('amount')
    def constraint_custody_amount(self):
        for rec in self:
            if rec.is_custody_payment:
                if rec.amount > rec.custody_remaining_amount:
                    raise ValidationError(_('Payment amount must be equal or less then custody amount'))

    def action_mark_custody_paid(self):
        if any(not payment.is_custody_payment for payment in self):
            raise ValidationError(_('Only custody payments can be marked as paid from this action.'))
        self.filtered(lambda payment: payment.state == 'in_process').action_validate()
        return True
