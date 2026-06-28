# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FinancialCustody(models.Model):
    _name = 'financial.custody'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Financial Custody'

    name = fields.Char(string="Custody No.", required=True, tracking=True, default='New')
    custody_amount = fields.Monetary(string="Custody Amount", required=True, tracking=True, currency_field='currency_id')
    paid_amount = fields.Monetary(string="Paid Amount", currency_field='currency_id', compute='_compute_payments_count')
    remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='currency_id', compute='_compute_payments_count')
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", default=lambda s: s.env.user.company_id.currency_id)
    reason = fields.Html(string="Reason", required=True, )
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('approved', 'First Approve'), ('second_approve', 'Second Approve'),
                                        ('rejected', 'Rejected'), ('canceled', 'Canceled'),
                                        ('open', 'Open'), ('validate', 'Validate')],
                             default='draft', tracking=True)
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")
    analytic_tags_ids = fields.Many2many(comodel_name="account.analytic.tag", relation="financial_custody_analytic_tags_rel", column1="custody_id",
                                         column2="analytic_tag_id", string="Analytic Tags", )
    due_date = fields.Date(string="Due Date", required=True, default=fields.Date.context_today)
    account_id = fields.Many2one(comodel_name="account.account", string="Account", related='partner_id.custody_account_id', store=True, readonly=False)
    move_id = fields.Many2one(comodel_name="account.move", string="Entry")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", default=lambda self: self.env.user.partner_id, required=True)
    payment_count = fields.Integer(compute='_compute_payments_count')
    reject_reason = fields.Text(string='Reject Reason')
    reject_step = fields.Char(string='Reject Step')
    reject_uid = fields.Many2one(comodel_name='res.users', string='Reject By')
    reject_date = fields.Date(string='Reject Date')
    installment_ids = fields.One2many(comodel_name='financial.custody.installment.line', inverse_name='custody_id', string='Installments')
    remaining_move_id = fields.Many2one(comodel_name='account.move', string='Remaining Move')

    @api.constrains('account_id')
    def constraint_partner_id(self):
        for rec in self:
            if rec.partner_id:
                if not rec.partner_id.custody_account_id:
                    raise ValidationError(_('Please set custody account on partner of employee'))

    @api.onchange('account_id')
    @api.depends('account_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.account_id = rec.partner_id.custody_account_id.id

    @api.constrains('reason')
    def check_constrains_reason(self):
        if self.reason == '<p><br></p>':
            raise UserError("Please, Add a reason!")

    def custody_action_validate(self):
        for rec in self:
            remaining_amount = rec.custody_amount - sum(rec.installment_ids.mapped('amount'))
            if remaining_amount > 0:
                credit_line = {
                    'account_id': rec.partner_id.custody_account_id.id,
                    'partner_id': rec.partner_id.id,
                    'name': f'Remaining Amount back to source from custody {rec.name}',
                    'debit': 0,
                    'credit': remaining_amount,
                    'date_maturity': fields.Date.today(),
                }
                debit_line = {
                    'account_id': rec.journal_id.default_account_id.id,
                    'partner_id': rec.partner_id.id,
                    'name': f'Remaining Amount back to source from custody {rec.name}',
                    'debit': remaining_amount,
                    'credit': 0,
                    'date_maturity': fields.Date.today(),
                }
                move_vals = {
                    'date': fields.Date.today(),
                    'journal_id': rec.journal_id.id,
                    'ref': rec.name,
                    'currency_id': rec.currency_id.id,
                    'move_type': 'entry',
                    'line_ids': [(0, 0, credit_line), (0, 0, debit_line)]
                }
                rec.remaining_move_id = self.env['account.move'].create(move_vals)
            if rec.installment_ids:
                for line in rec.installment_ids:
                    if not line.bill_id and line.account_id:
                        credit_line = {
                            'account_id': rec.partner_id.custody_account_id.id,
                            'partner_id': rec.partner_id.id,
                            'name': f'{line.note} / {line.due_date} / {rec.name}',
                            'debit': 0,
                            'credit': line.amount,
                            'amount_currency': remaining_amount,
                            'currency_id': rec.currency_id.id,
                            'date_maturity': fields.Date.today(),
                        }
                        debit_line = {
                            'account_id': line.account_id.id,
                            'partner_id': rec.partner_id.id,
                            'name': f'{line.note} / {line.due_date} / {rec.name}',
                            'debit': line.amount,
                            'credit': 0,
                            'amount_currency': -1 * remaining_amount,
                            'currency_id': rec.currency_id.id,
                            'date_maturity': fields.Date.today(),
                        }
                        move_vals = {
                            'date': fields.Date.today(),
                            'journal_id': rec.journal_id.id,
                            'ref': rec.name,
                            'currency_id': rec.currency_id.id,
                            'move_type': 'entry',
                            'line_ids': [(0, 0, credit_line), (0, 0, debit_line)]
                        }
                        line.move_id = self.env['account.move'].create(move_vals)
                        line.move_id.action_post()

                    if line.bill_id and not line.account_id:
                        payment = self.env['account.payment.register'].with_context(active_model='account.move',active_ids=line.bill_id.ids).create({
                            'amount': line.amount,
                            'group_payment': True,
                            'payment_difference_handling': 'open',
                            'payment_date': fields.Date.today(),
                            'currency_id': self.env.company.currency_id.id,
                            'journal_id': rec.journal_id.id,
                            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,

                        })._create_payments()
                new_payments = self.env['account.payment'].search([('is_custody_payment', '=', True), ('custody_id', '=', rec.id), ('state', '=', 'posted')])
                for invoice, payment in zip(rec.installment_ids.mapped('move_id')+rec.installment_ids.mapped('bill_id'), new_payments):
                    (invoice + payment.move_id).line_ids \
                        .filtered(lambda line: line.account_type in ('asset_receivable', 'liability_payable')).reconcile()
            rec.state = 'validate'

    def custody_first_approve(self):
        self.state = 'approved'

    def custody_second_approve(self):
        for rec in self:
            rec.state = 'second_approve'
            next_sequence = '/'
            if rec.name == 'New':
                next_sequence = self.env['ir.sequence'].next_by_code('financial.custody')
                rec.name = next_sequence
            payment_method_id = self.env.ref('account.account_payment_method_manual_out').id
            journal_id = rec.journal_id
            if not rec.journal_id:
                journal_id = self.env.ref('financial_custody.data_journal_custody')
            account_voucher_vals = {'move_type': 'entry', 'ref': next_sequence,
                                    'date': fields.Date.context_today(rec),
                                    'partner_id': rec.create_uid.partner_id.id,
                                    'preferred_payment_method_id': payment_method_id, 'journal_id': journal_id.id}
            if rec.partner_id:
                account_voucher_vals.update({'partner_id': rec.partner_id.id})
            line_ids = {'partner_id': rec.partner_id and rec.partner_id.id or False, 'name': next_sequence,
                        'analytic_distribution': {rec.analytic_account_id.id: 100} if rec.analytic_account_id else False,
                        'account_id': rec.account_id.id,
                        'debit': rec.custody_amount}
            credit_line_ids = {'partner_id': rec.partner_id and rec.partner_id.id or rec, 'name': next_sequence,
                               'analytic_distribution': {rec.analytic_account_id.id: 100} if rec.analytic_account_id else False,
                               'account_id': journal_id.default_account_id.id,
                               'credit': rec.custody_amount}
            account_voucher_vals.update({'line_ids': [(0, 0, line_ids), (0, 0, credit_line_ids)]})
            # move_id = rec.env['account.move'].create(account_voucher_vals)
            # rec.move_id = move_id.id

    def custody_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject',
            'res_model': 'financial.custody.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_custody_id': self.id
            }
        }

    def custody_action_open(self):
        self.state = 'open'

    def custody_cancel(self):
        self.state = 'cancelled'

    def _compute_payments_count(self):
        for rec in self:
            payments = self.env['account.payment'].search([('is_custody_payment', '=', True), ('custody_id', '=', rec.id), ('state', '=', 'posted')])
            rec.payment_count = len(payments)
            rec.paid_amount = sum(payments.mapped('amount'))
            rec.remaining_amount = rec.custody_amount - rec.paid_amount

    def action_open_custody_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'target': 'self',
            'domain': [('is_custody_payment', '=', True), ('custody_id', '=', self.id)],
            'context': {
                'default_payment_type': 'outbound',
                'default_partner_type': 'supplier',
                'default_destination_account_id': self.partner_id.custody_account_id.id,
                'default_journal_id': self.journal_id.id,
                'default_custody_id': self.id,
                'default_is_custody_payment': True,
                'default_custody_remaining_amount': self.remaining_amount,
                'default_partner_id': self.partner_id.id,
                'default_amount': self.remaining_amount,
                'create': False if self.remaining_amount == 0 else True
            }
        }

    @api.constrains('installment_ids')
    def check_constrains_installment_ids(self):
        for rec in self:
            if rec.installment_ids:
                if rec.custody_amount < sum(rec.installment_ids.mapped('amount')):
                    raise ValidationError(_('The installment amount must be equal or less then  custody amount'))


class CustodyRejectReasonWizard(models.TransientModel):
    _name = 'financial.custody.reject.wizard'

    custody_id = fields.Many2one(comodel_name='financial.custody', string='Custody')
    reason = fields.Text(required=True, string='Reason')

    def action_confirm(self):
        self.custody_id.state = 'rejected'
        self.custody_id.reject_reason = self.reason
        self.custody_id.reject_step = self.custody_id.state
        self.custody_id.reject_uid = self.env.uid
        self.custody_id.reject_date = fields.Date.today()


class CustodyInstallmentLine(models.Model):
    _name = 'financial.custody.installment.line'
    _description = 'Custody Installment Line'

    custody_id = fields.Many2one(comodel_name='financial.custody', string='Custody')
    due_date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount', required=True)
    note = fields.Text(string='Note', required=True)
    account_id = fields.Many2one(comodel_name='account.account', string='Account')
    move_id = fields.Many2one(comodel_name='account.move', string='Journal Entry')
    bill_id = fields.Many2one(comodel_name='account.move', string='Bill',
                              domain=[('move_type', '=', 'in_invoice'), ('state', '=', 'posted'), ('payment_state', '=', 'not_paid')])

    @api.onchange('bill_id')
    def onchange_bill_id(self):
        for rec in self:
            if rec.bill_id:
                rec.account_id = False

    @api.onchange('account_id')
    def onchange_account_id(self):
        for rec in self:
            if rec.bill_id:
                rec.bill_id = False
