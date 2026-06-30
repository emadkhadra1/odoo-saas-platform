# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"
    payment_type_check = fields.Selection([('payment', "Payment"),
                                           ('check', "Cheque"),
                                           ], default='payment', required=True, string='Payment Method (checks)')
    check_no = fields.Char('Check No.')
    def _prepare_payment_vals(self, invoices):
        active_id =self.env.context.get('active_id')
        so_id = self.env['account.move'].search([('id','=',active_id)]).sale_order
        move_id = self.env['account.move'].search([('id','=',active_id)])
        res = super(AccountPaymentRegister, self)._prepare_payment_vals(invoices)
        res.update({
            'payment_type_check': self.payment_type_check,
            'check_no': self.check_no,
            'so_id': so_id.id,
            'offer_id': so_id.id,
            'partner_invoice_id': self.env.context.get('active_id'),
            'analytic_account_id': move_id.line_ids.mapped('analytic_account_id').id,
            # 'unit_id': unit_id,
        })
        return res
    def _create_payment_vals_from_wizard(self):
        active_id =self.env.context.get('active_id')
        so_id = self.env['account.move'].search([('id','=',active_id)]).sale_order.id
        move_id = self.env['account.move'].search([('id','=',active_id)])
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        res.update({
            'payment_type_check': self.payment_type_check,
            'check_no': self.check_no,
            'so_id': so_id,
            'offer_id': so_id,
            'partner_invoices_id': self.env.context.get('active_id'),
            'analytic_account_id': move_id.invoice_line_ids.mapped('analytic_account_id').id,
        })
        return res

    @api.onchange('amount')
    def onchange_amount_greater_or_less(self):
        active_id =self.env.context.get('active_id')
        invoice_amount = self.env['account.move'].search([('id','=',active_id)]).amount_residual
        if self.amount and active_id:
            if self.amount > invoice_amount :
                raise exceptions.ValidationError('Amount must be equal to Invoice amount')
