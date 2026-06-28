# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from dateutil.relativedelta import relativedelta


class collect_wizard(models.TransientModel):
    _name = 'collect.wizard'

    date = fields.Date(string="Collect Date", default=fields.date.today(), required=False, )

    account_payment_id = fields.Many2one('account.payment', 'Check')
    line_ids = fields.One2many(comodel_name="collect.wizard.lines", inverse_name="collect_wizard_id", string="",
                               required=False, )

    def collect(self):
        for line in self.line_ids.filtered(lambda u: u.apply_fee):
            check_account = line.payment_id.partner_id.property_account_receivable_id.id
            if not line.analytic_account_id.fee_account:
                raise exceptions.ValidationError(_(
                    'There is no Fee Account defined on this Project.'))
            fee_account = line.analytic_account_id.fee_account.id

            my_list = []
            sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
            my_list.append((0, 0, {
                'name': str(line.payment_id.name),
                'account_id': check_account,
                'debit': line.fee_amount,
                'partner_id': line.payment_id.partner_id.id,
                'analytic_account_id': line.payment_id.analytic_account_id.id,
            }))
            my_list.append((0, 0, {
                'name': str(line.payment_id.name),
                'account_id': fee_account,
                'credit': line.fee_amount,
                'partner_id': line.payment_id.partner_id.id,
                'analytic_account_id': line.payment_id.analytic_account_id.id,
            }))
            move_id = self.env['account.move'].sudo().create({
                'ref': str(line.payment_id.name),
                'journal_id': line.analytic_account_id.fee_journal_id.id,
                'partner_id': line.payment_id.partner_id.id,
                'type': 'entry',
                'line_ids': my_list
            })
            for l in move_id.line_ids:
                l.write({
                    'payment_id': self.account_payment_id.id
                })
            line.payment_id.penalty_amount = line.fee_amount
            # move_id.action_post()
        self.action_check_collected()

    def action_check_collected(self):
        payment = self.env['account.payment'].browse(self.env.context.get('active_id'))
        # selected = 0
        if self.account_payment_id.payment_status == 'deposit' or self.account_payment_id.payment_status == 'recycle':
            if self.account_payment_id.check_deposit_id.bank_journal_id.default_account_id:
                account = self.account_payment_id.check_deposit_id.bank_journal_id.default_account_id.id
            else:
                raise exceptions.UserError(_("Missing Debit Account on bank journal"))

            if self.account_payment_id.check_deposit_id.bank_journal_id.credit_check_account_id:
                account_c = self.account_payment_id.check_deposit_id.bank_journal_id.credit_check_account_id.id
            else:
                raise exceptions.UserError(_("Missing Credit Check Account on bank journal"))

            move_lst = []

            move_lst.append((0, 0, {
                'name': str(self.account_payment_id.check_deposit_id.name),
                'account_id': account,
                'debit': self.account_payment_id.amount,
                'partner_id': self.account_payment_id.partner_id.id,
                'date': self.date,
            }))

            move_lst.append((0, 0, {
                'name': str(self.account_payment_id.check_deposit_id.name),
                'account_id': account_c,
                'credit': self.account_payment_id.amount,
                'partner_id': self.account_payment_id.partner_id.id,
                'date': self.date,
            }))
            move_id = self.env['account.move'].create({
                'ref': str(self.account_payment_id.name),
                'journal_id': self.account_payment_id.check_deposit_id.bank_journal_id.id,
                'line_ids': move_lst
            })
            for l in move_id.line_ids:
                l.write({
                    'payment_id': self.account_payment_id.id
                })

            move_id.action_post()
            for l in move_id.line_ids:
                l.write({
                    'date': self.date
                })
            # if payment.install_id:
            # # debit_bank_line = move_id.line_ids.filtered(lambda l: l.debit > 0)
            #     debit_bank_line = payment.install_id.line_ids.filtered(
            #         lambda l: l.debit > 0 and not l.reconciled)
            #     # acc_rec_line = payment.move_line_ids.filtered(
            #     #     lambda l: l.account_id == debit_bank_line.account_id and l.credit > 0 and not l.reconciled)
            #
            #     if payment.install_id.state != 'posted':
            #         raise ValidationError(_(
            #             'Please post draft invoice of "%s"') )
            #     # else:
            #     #     aml3 = acc_rec_line + debit_bank_line
            #         if len(aml3) > 1:
            #             aml3.reconcile()
            self.account_payment_id.payment_status = 'collected'
            self.account_payment_id.collected_date = self.date
            # line.select = False

    # @api.onchange('date')
    # def onchange_date(self):
    #     if self.date:
    #         for line in self.line_ids:
    #             analytic_account = line.analytic_account_id
    #             apply_penalty = self.check_apply_penalty(self.date, line.payment_id.due_date,
    #                                                      analytic_account.fee_percent_type)
    #             if apply_penalty:
    #                 fee_amount = self.calc_penalty_amount(analytic_account, self.date,
    #                                                       line.payment_id.due_date,
    #                                                       line.payment_id.amount)
    #                 line.fee_amount = fee_amount
    #             else:
    #                 line.fee_amount = 0.0

    def calc_penalty_amount(self, analytic_account, payment_date, due_date, amount):
        fee_amount = 0.0
        if analytic_account.fee_percent_type == 'daily':
            difference = relativedelta(payment_date, due_date)
            years = difference.years
            months = difference.months
            days = difference.days + (months * 30) + (years * 12 * 30)
            fee_amount = ((analytic_account.fee_percent / 100) / 365) * days * amount
        elif analytic_account.fee_percent_type == 'monthly':
            difference = relativedelta(payment_date, due_date)
            years = difference.years
            months = difference.months + (years * 12)
            fee_amount = ((analytic_account.fee_percent / 100) / 12) * months * amount
        return round(fee_amount, 2)

    def check_apply_penalty(self, current_date, date_due, penalty_type):
        if penalty_type == 'daily':
            date_due = date_due + timedelta(days=1)
            if date_due < current_date:
                return True
            else:
                return False
        else:
            date_due = date_due + relativedelta(months=1)
            if date_due < current_date:
                return True
            else:
                return False


class wizard_lines(models.TransientModel):
    _name = 'collect.wizard.lines'

    collect_wizard_id = fields.Many2one(comodel_name="collect.wizard", string="Collect Wizard", required=False, )
    payment_id = fields.Many2one(comodel_name="account.payment", string="Check payment", required=False, )
    apply_fee = fields.Boolean('Apply Fee')
    fee_percent = fields.Float('Fee Percent')
    fee_amount = fields.Float('Fee Amount')
    is_no_fee = fields.Boolean('No Fee')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    @api.onchange('fee_percent')
    def onchange_fee_percent(self):
        for rec in self:
            difference = date.today() - Date.from_string(rec.payment_id.due_date)

            if rec.analytic_account_id:
                fee_percent_type = rec.analytic_account_id.fee_percent_type
                if fee_percent_type == 'daily':
                    days = difference.days
                    rec.fee_amount = ((rec.fee_percent / 100) / 365) * days * rec.payment_id.amount
                elif fee_percent_type == 'monthly':
                    difference = relativedelta(date.today(), Date.from_string(rec.payment_id.due_date))
                    months = difference.months
                    rec.fee_amount = ((rec.fee_percent / 100) / 12) * months * rec.payment_id.amount
