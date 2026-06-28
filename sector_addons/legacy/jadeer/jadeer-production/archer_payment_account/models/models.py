# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

class AccountMove(models.Model):
    _inherit = "account.move"
    state = fields.Selection(selection_add=[('draft',), ('approved', 'Approved'),('posted',) ], ondelete={'approved': 'cascade'})

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    @api.onchange('amount')
    def compute_limit_amount(self):
        lines = self.env['account.move'].browse(self._context.get('active_ids', []))
        for rec in lines:
            if self.amount > rec.amount_residual:
                raise exceptions.ValidationError('Payment amount Cannot be Greater than Invoice amount')
    def _create_payments(self):
        lines = self.env['account.move'].browse(self._context.get('active_ids', []))
        for rec in lines:
            if self.amount > rec.amount_residual:
                raise exceptions.ValidationError('Payment amount Cannot be Greater than Invoice amount')
        res = super(AccountPaymentRegister, self)._create_payments()
        return res

class AccountPayments(models.Model):
    _inherit = "account.payment"
    _inherits = {'account.move': 'move_id'}
    def approve_payment_transfer(self):
        self.write({'state':'approved'})