# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class Payment(models.Model):
    _inherit = 'account.payment'

    is_notes_pay = fields.Boolean(string='Is Notes Payable', related="journal_id.is_notes_pay", store=True)
    issue_bank_account_id = fields.Many2one(comodel_name="account.account", string="Issue Bank Account")
    _sql_constraints = [
        ('unique_check_issue_bank', 'unique (check_no,issue_bank_account_id)',
         "Check # unique per Issue Bank Account .")
    ]

    payment_status = fields.Selection(selection_add=[
        ('withdraw', 'Withdraw')
    ])
    check_remain_amount = fields.Monetary(string="Check Remain Amount", compute="calc_check_remain_amount", store=True)

    @api.depends('journal_id')
    @api.onchange('journal_id')
    def onchange_journal_issue_account_id(self):
        for rec in self:
            if rec.journal_id.is_notes_pay:
                rec.issue_bank_account_id = rec.journal_id.issue_bank_account_id.id
    @api.depends('line_ids.matched_credit_ids')
    def calc_check_remain_amount(self):
        for pay in self:
            pay.check_remain_amount = pay.amount - sum(pay.line_ids.matched_credit_ids.mapped('amount'))

    def action_issued_check_return(self):
        # for payment in self:
        #     if payment.payment_status == 'posted':
        #         if payment.journal_id.inbound_payment_method_line_ids[0]:
        #             debit_account = payment.journal_id.inbound_payment_method_line_ids[0].payment_account_id
        #         else:
        #             raise UserError(_("Missing Debit Account on {} journal".format(payment.journal_id.name)))
        #         if payment.journal_id.issue_return_account_id:
        #             credit_account = payment.journal_id.issue_return_account_id
        #         else:
        #             raise UserError(_("Missing Return Account On Journal {}".format(payment.journal_id.name)))
        #         move_vals = payment.prepare_payment_vals(debit_account, credit_account)
        #         move_id = payment.env['account.move'].create(move_vals)
        #         move_id.action_post()
        #         payment.payment_status = 'withdraw'
        return {
            'name': "Return Date",
            'view_mode': 'form',
            'res_model': 'return.cheque.date',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_payment_id': self.id
            },
        }
    def action_check_withdraw(self):
        for payment in self:
            withdraw_move_id = payment.create_withdraw_move()
            # reconcile_move_id = payment.create_reconcile_move()
            payment_debit_account_id = payment.journal_id.inbound_payment_method_line_ids[0].payment_account_id
            payment_credit_account_id = payment.journal_id.outbound_payment_method_line_ids[0].payment_account_id
            # advance_payment_account_id = payment.partner_id.advance_payment_account_id
            payment_credit_credit_lines = (payment.move_id + withdraw_move_id).mapped('line_ids').filtered(
                lambda l: l.account_id in [payment_debit_account_id, payment_credit_account_id])
            payment_credit_credit_lines.reconcile()
            # advance_payment_lines = (payment.move_id + reconcile_move_id).mapped('line_ids').filtered(
            #     lambda l: l.account_id in [advance_payment_account_id])
            # advance_payment_lines.reconcile()
            payment.payment_status = 'withdraw'

    def create_withdraw_move(self):
        move_id = self.env['account.move']
        if self.payment_status == 'posted':
            if self.journal_id.inbound_payment_method_line_ids[0]:
                debit_account = self.journal_id.inbound_payment_method_line_ids[0].payment_account_id
            else:
                raise UserError(_("Missing Debit Account on {} journal".format(self.journal_id.name)))
            if self.issue_bank_account_id:
                credit_account = self.issue_bank_account_id
            else:
                raise UserError(_("Missing Issue Bank Account on this check !"))
            move_vals = self.prepare_move_vals(debit_account, credit_account)
            move_id = self.env['account.move'].create(move_vals)
            move_id.action_post()
        return move_id

    def create_reconcile_move(self):
        move_id = self.env['account.move']
        if self.payment_status == 'posted':
            if self.partner_id.property_account_payable_id:
                debit_account = self.partner_id.property_account_payable_id
            else:
                raise UserError(_("Missing Payable Account on Vendor"))
            if self.partner_id.advance_payment_account_id:
                credit_account = self.partner_id.advance_payment_account_id
            else:
                raise UserError(_("Missing Advance Payment Account on Vendor"))
            move_vals = self.prepare_move_vals(debit_account, credit_account)
            move_id = self.env['account.move'].create(move_vals)
            move_id.action_post()
        return move_id

    def prepare_move_vals(self, debit_account, credit_account, ref=False, amount=False):
        vals = {
            'ref': ref if ref else self.name,
            'journal_id': self.journal_id.id,
            'payment_id': self.id,
            "line_ids": [
                (0, 0, self._prepare_move_line_vals('debit', debit_account, amount)),
                (0, 0, self._prepare_move_line_vals('credit', credit_account, amount))
            ]
        }
        return vals

    def _prepare_move_line_vals(self, typ, account_id, amount=False):
        line_vals = {
            'name': str(self.name),
            'account_id': account_id.id,
            'partner_id': self.partner_id.id,
        }
        if typ == 'debit':
            line_vals.update({
                'debit': amount if amount else self.amount,
            })
        else:
            line_vals.update({
                'credit': amount if amount else self.amount,
            })
        return line_vals

    #############################
    # Default Function Override #
    #############################
    # @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer')
    # def _compute_destination_account_id(self):
    #     super(Payment, self)._compute_destination_account_id()
    #     for pay in self:
    #         if pay.payment_type_check == 'check' and pay.payment_type == 'outbound' :
    #             pay.destination_account_id = pay.destination_account_id.id
    #         if pay.payment_type_check == 'check' and pay.payment_type == 'inbound' :
    #             pay.destination_account_id = pay.partner_id.property_account_receivable_id.id
    #             #
                #     # and pay.is_notes_pay and pay.partner_id.is_advance_payment_client and pay.partner_id.advance_payment_account_id:
                # pay.destination_account_id = pay.partner_id.advance_payment_account_id
