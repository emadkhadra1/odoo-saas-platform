# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta


class AccountMoveInherited(models.Model):
    _inherit = "account.move"

    is_unit_cost = fields.Boolean('Unit Cost')
    is_cost_entry = fields.Boolean('Cost Entry')
    unit_id = fields.Many2one('product.template', string='Unit')
    check = fields.Boolean()
    sale_order = fields.Many2one('sale.order')
    sale_order_line = fields.Many2one('sale.order.line')
    date_temp = fields.Date('Due Temp')
    collect_date = fields.Date('Collect Date')
    state = fields.Selection(readonly=False)
    # pay_type = fields.Char()
    pay_type = fields.Selection(
        [('contracting', 'DownPayment'), ('delivery', 'Delivery'),('maintenance','Maintenance'),
         ('installment', 'Installment'), ('reservation', 'Reservation')], default='contracting', string='Type')
    utility_invoice = fields.Boolean(default=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        super(AccountMoveInherited, self)._compute_amount()
        for rec in self:
            if rec.unit_id and rec.pay_type == 'contracting' and rec.payment_state in ['paid','in_payment']\
                    and rec.amount_residual == 0:
                rec.unit_id.action_book_product()
                rec.unit_id.sudo().update({'state':'deal'})
                rec.sale_order.opportunity_id.write({'stage_id':self.env.ref('real_estate_crm.stage_done_deal').id})
            elif rec.unit_id and rec.pay_type == 'contracting' and rec.payment_state in ['partial']\
                    and rec.amount_residual >= 0:
                # rec.unit_id.action_book_product()
                rec.unit_id.sudo().update({'state':'contract'})
            # if rec.unit_id and rec.pay_type == 'reservation' and rec.payment_state in ['paid','in_payment']\
            #         and rec.amount_residual == 0:
            #     rec.unit_id.action_book_product()

    def action_invoice_register_payment(self):
        res = super(AccountMoveInherited, self).action_invoice_register_payment()
        if self.move_type == 'out_invoice':
            if res.get('context'):
                ctx = dict(res.get('context'))
                ctx.update({'default_analytic_account_id': self.analytic_account_id.id, 'default_install_id': self.id})
                res['context'] = ctx
            else:
                context = {'default_analytic_account_id': self.analytic_account_id.id, 'default_install_id': self.id}
                res['context'] = context
        return res

    @api.onchange('analytic_account_id', 'invoice_line_ids')
    def _onchange_analytic_account_id(self):
        for invoice in self:
            if invoice.analytic_account_id:
                if invoice.invoice_line_ids:
                    for line in invoice.invoice_line_ids:
                        line.analytic_account_id = invoice.analytic_account_id

    def _recompute_payment_terms_lines(self):
        ''' Compute the dynamic payment term lines of the journal entry.'''
        self.ensure_one()
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_context(force_company=self.journal_id.company_id.id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    return self.partner_id.property_account_receivable_id
                else:
                    return self.partner_id.property_account_payable_id
            else:
                # Search new account.
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=',
                     'receivable' if self.type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                ]
                return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date,
                                                                  currency=self.currency_id)
                if self.currency_id != self.company_id.currency_id:
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date,
                                                                               currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
                else:
                    # Single-currency.
                    return [(b[0], b[1], 0.0) for b in to_compute]
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                if self.journal_id.company_id.currency_id.is_zero(balance) and len(to_compute) > 1:
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                        'account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                        'account_id': account.id,
                        'analytic_account_id': self.analytic_account_id.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate._onchange_amount_currency()
                    candidate._onchange_balance()
            return new_terms_lines

        existing_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = self.company_id.currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity

    def action_post(self):
        # OVERRIDE
        # Auto-reconcile the invoice with payments coming from transactions.
        # It's useful when you have a "paid" sale order (using a payment transaction) and you invoice it later.
        res = super(AccountMoveInherited, self).action_post()
        if not self:
            return res
        for invoice in self:
            if invoice.unit_id:
                invoice.unit_id.min_deposit_amount_temp = invoice.unit_id.min_deposit_amount
                invoice.unit_id.customer_id = invoice.partner_id.id
                invoice.unit_id.booked_date = datetime.date.today()
            payments = invoice.mapped('transaction_ids.payment_id')
            move_lines = payments.mapped('invoice_line_ids').filtered(
                lambda line: not line.reconciled and line.credit > 0.0)
            for line in move_lines:
                invoice.invoice_outstanding_credits_debits_widget(line.id)
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    utility_id = fields.Many2one(comodel_name="product.utility")

    @api.onchange('utility_id')
    def change_domain(self):
        if self.move_id.utility_invoice:
            return {'domain': {'product_id':
                                   [('sale_ok', '=', True), '|', ('company_id', '=', False),
                                    ('company_id', '=', self.move_id.company_id.id)] or
                                   [('purchase_ok', '=', True), '|', ('company_id', '=', False),
                                    ('company_id', '=', self.move_id.company_id.id)]}}
        else:
            return {'domain': {'product_id':
                                   self.env.context.get('default_move_type') in ('out_invoice', 'out_refund', 'out_receipt') and
                                   [('sale_ok', '=', True), '|', ('company_id', '=', False),
                                    ('company_id', '=', self.move_id.company_id.id)] or
                                   [('purchase_ok', '=', True), '|', ('company_id', '=', False),
                                    ('company_id', '=', self.move_id.company_id.id)]}}
