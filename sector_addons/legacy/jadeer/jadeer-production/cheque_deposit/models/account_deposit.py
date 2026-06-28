# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountCheckDeposit(models.Model):
    _name = "account.check.deposit"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Account Cheque Deposit"
    _order = 'deposit_date desc'

    name = fields.Char(string='Name', size=64, readonly=True, default='/', copy=False)
    check_payment_ids = fields.One2many(
        'account.payment', 'check_deposit_id', string='Cheque Payments')
    deposit_date = fields.Date(
        string='Deposit Date', required=True,
        states={'done': [('readonly', '=', True)]},
        default=fields.Date.context_today)

    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        domain=[('type', '=', 'bank'), ('bank_account_id', '=', False)],
        required=True, states={'done': [('readonly', '=', True)]})
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        states={'done': [('readonly', '=', True)]})
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Done'),

        ], string='Status', default='draft', readonly=True)
    move_id = fields.Many2one(
        'account.move', string='Journal Entry', readonly=True)
    bank_journal_id = fields.Many2one(
        'account.journal', string='Bank Account', required=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'bank'), ('is_notes_rec', '=', True)]",
        states={'done': [('readonly', '=', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        states={'done': [('readonly', '=', True)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'account.check.deposit'))

    total_amount = fields.Float(
        compute='_compute_check_deposit',
        string="Total Amount", readonly=True,
    )
    check_count = fields.Integer(
        compute='_compute_check_deposit', readonly=True,
        string="Number of Cheques")

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence']. \
                next_by_code('account.check.deposit')
        return super(AccountCheckDeposit, self).create(vals)

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.currency_id:
                self.currency_id = self.journal_id.currency_id
            else:
                self.currency_id = self.journal_id.company_id.currency_id

    @api.depends('check_payment_ids.amount', 'check_payment_ids')
    def _compute_check_deposit(self):
        for deposit in self:
            total = count = 0.0
            for line in deposit.check_payment_ids:
                count += 1
                total += line.amount
            deposit.total_amount = total
            deposit.check_count = count

    @api.model
    def _prepare_account_move_vals(self, deposit):
        journal_id = deposit.journal_id.id
        move_vals = {
            'journal_id': journal_id,
            'date': deposit.deposit_date,
            'ref': deposit.name,
        }
        return move_vals

    @api.model
    def _prepare_move_line_vals(self, line):
        return {
            'name': _('Check Deposit - Ref. Check %s') % line.name,
            'credit': line.amount,
            'payment_id': line.id,
            'debit': 0.0,
            'account_id': self.journal_id.inbound_payment_method_line_ids[0].payment_account_id.id,
            'partner_id': line.partner_id.id,
            'currency_id': line.currency_id.id if line.company_id.currency_id != line.currency_id else False,
            'amount_currency': line.amount * -1 if line.company_id.currency_id != line.currency_id else 0,
        }

    @api.model
    def _prepare_counterpart_move_lines_vals(self, deposit, line):
        if deposit.bank_journal_id.debit_check_account_id:
            account_id = deposit.bank_journal_id.debit_check_account_id.id
        else:
            raise UserError(_("Missing Cheque Debit Account on bank journal"))

        return {
            'name': _('Check Deposit - Ref. Check %s') % line.name,
            'payment_id': line.id,
            'debit': line.amount,
            'credit': 0.0,
            'account_id': account_id,
            'partner_id': line.partner_id.id,
            'currency_id': deposit.currency_id.id if deposit.company_id.currency_id != deposit.currency_id else False,
            'amount_currency': line.amount if deposit.company_id.currency_id != deposit.currency_id else 0,

        }

    def validate_deposit(self):
        am_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        for deposit in self:
            if len(deposit.check_payment_ids) == 0:
                raise ValidationError("Can't validate deposit, there's no payments to deposit")
            move_vals = self._prepare_account_move_vals(deposit)
            move = am_obj.create(move_vals)
            total_amount = 0.0
            for line in deposit.check_payment_ids:
                total_amount += line.amount
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line_obj.with_context(check_move_validity=False).create(line_vals)
                line_deb_vals = self._prepare_counterpart_move_lines_vals(deposit, line)
                line_deb_vals['move_id'] = move.id
                move_line_obj.create(line_deb_vals)
                line.payment_status = 'deposit'
            move.action_post()
            deposit.write({'state': 'done', 'move_id': move.id})
        return True
