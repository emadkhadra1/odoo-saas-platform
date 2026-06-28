# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class AccountCheckCash(models.Model):
    _name = "account.check.cash"

    cash_journal_id = fields.Many2one(
        'account.journal', string='Journal',
        domain=[('type', '=', 'cash')], required=1)

    payment_id = fields.Many2one(
        'account.payment', string='Payment Cheque')

    def create_cash_move(self):
        if self.payment_id:
            if self.payment_id.payment_status == 'returned':
                if self.cash_journal_id.inbound_payment_method_line_ids[0]:
                    debit_account = self.cash_journal_id.inbound_payment_method_line_ids[0].payment_account_id.id
                else:
                    raise UserError(_(
                        'Please Add  Debit account for this Journal .'))

                if self.payment_id.check_deposit_id.bank_journal_id.return_credit_check_account_id:
                    credit_account = self.payment_id.check_deposit_id.bank_journal_id.return_credit_check_account_id.id
                else:
                    raise UserError(_("Missing Return Check Credit Account on bank journal"))

                move_id = self.env['account.move'].create({
                    'ref': str(self.payment_id.check_deposit_id.name),
                    'journal_id': self.payment_id.check_deposit_id.bank_journal_id.id,
                    'payment_id': self.payment_id.id,
                })

                sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': str(self.payment_id.name),
                    'account_id': debit_account,
                    'debit': self.payment_id.amount,
                    'move_id': move_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': str(self.payment_id.name),
                    'account_id': credit_account,
                    'credit': self.payment_id.amount,
                    'move_id': move_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                })
                move_id.action_post()
                self.payment_id.payment_status = 'cash'
