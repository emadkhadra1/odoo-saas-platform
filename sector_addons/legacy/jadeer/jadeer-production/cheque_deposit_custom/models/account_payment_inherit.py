# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
import datetime
import logging
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class AccountCheckPayment(models.Model):
    _inherit = "account.payment"

    transfer_move_id = fields.Many2one('account.move',string='Transfer Entry')
    return_move_id = fields.Many2one('account.move',string='Return Entry')
    exclude_from_deposit = fields.Boolean(string='Excluded',compute='compute_exclude_from_deposit',store=True)
    @api.depends('has_reconciled_entries')
    def compute_exclude_from_deposit(self):
        for rec in self:
            rec.exclude_from_deposit = rec.has_reconciled_entries
    def return_check(self):
        if self.transfer_move_id:
            move = self.transfer_move_id.copy()
            debit_line = move.line_ids.filtered(lambda x:x.debit>0)
            debit_acc = debit_line.account_id.id
            credit_line = move.line_ids.filtered(lambda x:x.credit>0)
            credit_acc = credit_line.account_id.id
            debit_line.account_id = credit_acc
            credit_line.account_id = debit_acc
            move.post()
            self.return_move_id=move.id

    def transfer_check(self):
        return {
            'name': 'Transfer Check',
            'view_mode': 'form',
            'res_model': 'transfer.check',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
            },
        }

