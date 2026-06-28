# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class transfercheck(models.Model):
    _name = "transfer.check"
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor')
    payment_id = fields.Many2one(
        'account.payment', string='Check')

    def apply(self):
        if self.vendor_id:
            if not self.payment_id.transfer_move_id:
                if self.vendor_id.property_account_payable_id:
                    debit_account = self.vendor_id.property_account_payable_id.id
                else:
                    raise UserError(_(
                        'Please Define  payable account for this Vendor.'))

                if self.payment_id.journal_id.inbound_payment_method_line_ids[0]:
                    credit_account = self.payment_id.journal_id.inbound_payment_method_line_ids[0].payment_account_id.id
                else:
                    raise UserError(_("Missing Outstanding receipt Account on journal"))

                move_id = self.env['account.move'].create({
                    'ref': self.payment_id.name,
                    'journal_id': self.payment_id.journal_id.id,
                })

                move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                move_lines.create({
                    'name': self.payment_id.check_no or str(self.payment_id.name),
                    'account_id': debit_account,
                    'debit': self.payment_id.amount,
                    'move_id': move_id.id,
                    'partner_id': self.vendor_id.id,
                })
                move_lines.create({
                    'name': self.payment_id.check_no or str(self.payment_id.name),
                    'account_id': credit_account,
                    'credit': self.payment_id.amount,
                    'move_id': move_id.id,
                    'partner_id': self.vendor_id.id,
                })
                move_id.action_post()
                self.payment_id.transfer_move_id = move_id.id
