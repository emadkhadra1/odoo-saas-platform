# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
import datetime
import logging
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        if self.payment_id and self.payment_id.state == 'draft':
            self.payment_id.action_post()
        else:
            self._post(soft=False)
        return False
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.journal_id.type_of_check == 'utility':
            new_term_account = self.journal_id.utility_account_receivable_id
        else:
            new_term_account = None
        for line in self.line_ids:
            if new_term_account and line.account_id.user_type_id.type in ('receivable', 'payable'):
                line.account_id = new_term_account
        return res
class AccountCheckPayment(models.Model):
    _inherit = "account.payment"
    _description = "Account Cheque Payment"
    _order = 'due_date desc'
    partner_invoices_id = fields.Many2one('account.move','Invoices')
    
    @api.onchange('type_of_check')
    def multi_action_force_check_collected(self):
        for payment in self:
            if payment.partner_invoices_id:
                # payment.payment_status = 'collected'
                # payment.collected_date = payment.payment_date
                cr_payment_mv_line = payment.line_ids.filtered(
                    lambda line: not line.reconciled and line.credit > 0.0)
                if cr_payment_mv_line.move_id.state == 'draft':
                    cr_payment_mv_line.move_id.post()
                db_inv_mv_line = payment.partner_invoices_id.line_ids.filtered(lambda l: l.debit > 0.0 and not l.reconciled)
                if payment.partner_invoices_id.state == 'draft':
                    payment.partner_invoices_id.action_post()
                aml3 = cr_payment_mv_line
                if len(aml3) > 1:
                    aml3.reconcile()
                    payment.is_reconciled_collected = True
    def _default_my_date(self):
        return fields.Date.context_today(self)

    date_now = fields.Date(default=_default_my_date)
    due_date = fields.Date(string='Due Date')
    payment_id = fields.Many2one('account.payment')
    recheck_payment_id = fields.Many2one('account.payment')
    partner_bank = fields.Many2one('res.bank', string='Partner Bank')
    recheck_move_line_id = fields.Many2one('account.move.line')
    current_state = fields.Selection([
        ('collected', "Collected"),
        ('not_collected', "Not Collected"),
        ('paid', "Paid"),
    ], default='not_collected', readonly=True, string='Current State', copy=False)
    check_deposit_id = fields.Many2one(
        'account.check.deposit', string='Cheque Deposit', copy=False)
    re_check_deposit_id = fields.Many2one(
        'account.check.deposit', string='Cheque Deposit')
    is_current_week = fields.Boolean(compute="_check_current_month", store=True, default=False)
    re_check = fields.Boolean(string="Re-Check", store=True, readonly=True)
    check_no = fields.Char(string='Check #', copy=False)

    type_of_check = fields.Selection([('reservation','Reservation'),('utility', 'Utility'),('installment', 'Installment')],
                                     string='Type of Check')
    check_ty = fields.Selection([('check', 'شيك قضايا'), ('check2', 'شيك أمانات')],
                                string='Check',store=True)

    @api.onchange('journal_id')
    def journal_type_of_check(self):
        if self.journal_id:
            if self.journal_id.type_of_check:
                self.type_of_check = self.journal_id.type_of_check
    _sql_constraints = [
        ('unique_check_no_partner_bank', 'UNIQUE(check_no,partner_bank)',
         'check number related bank partner must be unique !')
    ]

    def cash_move(self):
        compose_form = self.env.ref('cheque_deposit.account_check_cash')
        return {
            'name': 'Cash Checks',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.check.cash',
            'type': 'ir.actions.act_window',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
            },
        }

    @api.depends('due_date', 'payment_type_check')
    def _check_current_month(self):
        for rec in self:
            if rec.payment_type_check == 'check':
                if str(rec.due_date) < (datetime.datetime.now() + relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if str(rec.due_date) >= datetime.datetime.now().strftime('%Y-%m-%d'):
                        rec.is_current_week = True
            else:
                rec.is_current_week = False

    def force_quotation_send(self):
        for order in self:
            email_act = order.send_mail_template()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.company_id.email)
                order.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    def unlink_move_line(self):
        if self.payment_status != 'posted':
            raise UserError('You cannot do this modification on a that move.')
        else:
            self.check_deposit_id = False

    def action_check_collected(self):
        for rec in self:
            if rec.payment_status == 'deposit' or rec.payment_status == 'recycle':
                # if rec.check_deposit_id.bank_journal_id.payment_debit_account_id:
                if rec.check_deposit_id.bank_journal_id.default_account_id:
                    account = rec.check_deposit_id.bank_journal_id.default_account_id.id
                else:
                    raise UserError(_("Missing Bank Account on bank journal"))

                if rec.check_deposit_id.bank_journal_id.credit_check_account_id:
                    account_c = rec.check_deposit_id.bank_journal_id.credit_check_account_id.id
                else:
                    raise UserError(_("Missing Credit Check Account on bank journal"))

                move_id = self.env['account.move'].create({
                    'ref': str(rec.name),
                    'journal_id': rec.check_deposit_id.bank_journal_id.id,
                    'payment_id': rec.id,
                })
                sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': str(rec.check_deposit_id.name),
                    'account_id': account,
                    'debit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': str(rec.check_deposit_id.name),
                    'account_id': account_c,
                    'credit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                move_id.action_post()
                rec.payment_status = 'collected'

    def action_check_returned(self):
        for rec in self:
            if rec.payment_status == 'deposit' or rec.payment_status == 'recycle':
                if rec.check_deposit_id.bank_journal_id.return_debit_check_account_id:
                    debit_return_account = rec.check_deposit_id.bank_journal_id.return_debit_check_account_id.id
                else:
                    raise UserError(_("Missing Return Check Debit Account on bank journal"))

                if rec.check_deposit_id.bank_journal_id.credit_check_account_id:
                    credit_check_account = rec.check_deposit_id.bank_journal_id.credit_check_account_id.id
                else:
                    raise UserError(_("Missing Credit Check Account on bank journal"))

                move_id = self.env['account.move'].create({
                    'ref': str(rec.check_deposit_id.name),
                    'journal_id': rec.check_deposit_id.bank_journal_id.id,
                    'payment_id': rec.id,
                })

                sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': "Return " + str(rec.check_deposit_id.name),
                    'account_id': debit_return_account,
                    'debit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': "Return " + str(rec.check_deposit_id.name),
                    'account_id': credit_check_account,
                    'credit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                # move_id.action_post()
                rec.payment_status = 'returned'

    def recycle_move(self):
        for rec in self:
            if rec.payment_status == 'returned':
                if rec.check_deposit_id.bank_journal_id.return_credit_check_account_id:
                    credit_return_account = rec.check_deposit_id.bank_journal_id.return_credit_check_account_id.id
                else:
                    raise UserError(_("Missing Return Check Credit Account on bank journal"))

                if rec.check_deposit_id.bank_journal_id.debit_check_account_id:
                    debit_check_account = rec.check_deposit_id.bank_journal_id.debit_check_account_id.id
                else:
                    raise UserError(_("Missing Debit Check Account on bank journal"))

                move_id = self.env['account.move'].create({
                    'ref': str(rec.check_deposit_id.name),
                    'journal_id': rec.check_deposit_id.bank_journal_id.id,
                    'payment_id': rec.id,
                })

                sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': "Recycle " + str(rec.check_deposit_id.name),
                    'account_id': debit_check_account,
                    'debit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': "Recycle " + str(rec.check_deposit_id.name),
                    'account_id': credit_return_account,
                    'credit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                move_id.action_post()
                rec.payment_status = 'recycle'

    def writeoff_move(self):
        for rec in self:
            if rec.payment_status == 'returned':
                if rec.check_deposit_id.bank_journal_id.bad_debit_account_id:
                    debit_account = rec.check_deposit_id.bank_journal_id.bad_debit_account_id.id
                else:
                    raise UserError(_(
                        'Please Add Bad Debit Account for this Journal .'))

                if rec.check_deposit_id.bank_journal_id.return_credit_check_account_id:
                    credit_account = rec.check_deposit_id.bank_journal_id.return_credit_check_account_id.id
                else:
                    raise UserError(_("Missing Return Check Credit Account on bank journal"))

                move_id = rec.env['account.move'].create({
                    'ref': str(rec.check_deposit_id.name),
                    'journal_id': rec.check_deposit_id.bank_journal_id.id,
                    'payment_id': rec.id,
                })

                sale_move_lines = rec.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': "Write-off " + str(rec.name),
                    'account_id': debit_account,
                    'debit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': "Write-off " + str(rec.name),
                    'account_id': credit_account,
                    'credit': rec.amount,
                    'move_id': move_id.id,
                    'partner_id': rec.partner_id.id,
                })
                move_id.action_post()
                rec.payment_status = 'writeoff'

    def recheck_move(self):
        for rec in self:
            partner = rec.partner_id.id
            amount = rec.amount
            return {
                'name': 'Re-Check Checks',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_payment_type': 'inbound',
                    'default_payment_type_check': 'check',
                    'default_partner_id': partner,
                    'default_currency_id': rec.currency_id.id,
                    'default_re_check': True,
                    'default_payment_method_id': rec.env.ref('account.account_payment_method_manual_in').id,
                    'default_journal_id': rec.journal_id.id,
                    'default_amount': amount,
                    'default_recheck_payment_id': rec.id,
                }
            }

    @api.model
    def create(self, vals):
        res = super(AccountCheckPayment, self).create(vals)
        if res.re_check == True:
            res.amount = res.recheck_payment_id.amount
            res.recheck_payment_id.payment_status = 're-check'
        return res

    def _prepare_payment_moves(self):
        res = super(AccountCheckPayment, self)._prepare_payment_moves()
        if self.check_no:
            for move in res:
                if move:
                    move.update({'ref': self.check_no})
        return res

    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['|',('payment_id', '=', self.id),('move_id', '=', self.check_deposit_id.move_id.id)],
        }
    def action_check_returned_to_partner(self):
        return {
            'name': "Return Date",
            'view_mode': 'form',
            'res_model': 'return.cheque.partner.date',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_payment_id': self.id
            },
        }
    def action_check_returned_to_pay(self):
        return {
            'name': "Return Date",
            'view_mode': 'form',
            'res_model': 'return.cheque.pay.date',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_payment_id': self.id
            },
        }
