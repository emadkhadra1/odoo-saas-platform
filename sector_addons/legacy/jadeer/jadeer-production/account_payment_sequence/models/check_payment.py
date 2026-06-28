# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import datetime
import logging
from odoo import api, fields, models, tools
from datetime import date
import calendar
import datetime
import time
from dateutil.relativedelta import relativedelta


class BankStatement(models.Model):
    _inherit = 'account.bank.statement'

    sequence = fields.Char(string="", required=False, )

    @api.model
    def create(self, vals):
        if vals.get('journal_id'):
            journal_id = self.env['account.journal'].browse(vals.get('journal_id'))
            if journal_id.payment_sequence_id.code:
                vals['sequence'] = self.env['ir.sequence'].next_by_code(journal_id.payment_sequence_id.code)
        return super(BankStatement, self).create(vals)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            if rec.journal_id.payment_sequence_id or rec.journal_id.receive_payment_sequence_id:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    rec.write({'name': name})

                elif rec.payment_type == 'outbound' and rec.journal_id.payment_sequence_id:
                    sequence_code = rec.journal_id.payment_sequence_id.code
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    rec.write({'name': name})

                elif rec.payment_type == 'inbound' and rec.journal_id.receive_payment_sequence_id:
                    sequence_code = rec.journal_id.receive_payment_sequence_id.code
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    rec.write({'name': name})
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                    name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.date)
                    rec.write({'name':name})
                if not (rec.journal_id.payment_sequence_id or rec.journal_id.receive_payment_sequence_id) and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
        return res
