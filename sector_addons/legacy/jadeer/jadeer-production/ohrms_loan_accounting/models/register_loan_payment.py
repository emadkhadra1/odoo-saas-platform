# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields
from odoo.exceptions import UserError


class wizard_model(models.TransientModel):
    _name = 'register.loan.payment'
    _description = 'Loan Payment'

    loan_id = fields.Many2one(comodel_name="hr.loan", string="Loan", )
    unpaid_amount = fields.Float(string="Unpaid Amount", )
    journal_id = fields.Many2one('account.journal', string="Journal")
    amount_to_pay = fields.Float(string="Amount To Pay", required=False, )

    def action_pay_loan(self):
        if not self.loan_id.employee_account_id or not self.loan_id.treasury_account_id or not self.journal_id:
            raise UserError("You must enter employee account & Treasury account and journal to approve ")
        if not self.loan_id.loan_lines:
            raise UserError('You must compute Loan Request before Approved')
        timenow = time.strftime('%Y-%m-%d')
        amount = self.amount_to_pay
        loan_name = self.loan_id.employee_id.name
        reference = self.loan_id.name
        journal_id = self.journal_id.id
        debit_account_id = self.loan_id.treasury_account_id.id
        credit_account_id = self.loan_id.employee_account_id.id
        debit_vals = {
            'name': loan_name,
            'account_id': debit_account_id,
            'journal_id': journal_id,
            'partner_id': self.loan_id.employee_id.address_id.id,
            'date': timenow,
            'debit': amount > 0.0 and amount or 0.0,
            'credit': amount < 0.0 and -amount or 0.0,
            'loan_id': self.loan_id.id,
        }
        credit_vals = {
            'name': loan_name,
            'account_id': credit_account_id,
            'journal_id': journal_id,
            'partner_id': self.loan_id.employee_id.address_id.id,
            'date': timenow,
            'debit': amount < 0.0 and -amount or 0.0,
            'credit': amount > 0.0 and amount or 0.0,
            'loan_id': self.loan_id.id,
        }
        vals = {
            'narration': loan_name,
            'ref': reference,
            'journal_id': journal_id,
            'partner_id': self.loan_id.employee_id.address_id.id,
            'date': timenow,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        }
        move = self.env['account.move'].create(vals)
        move.post()
        if move:
            lines = self.loan_id.loan_lines.filtered(lambda l: not l.paid).sorted(key='date', reverse=False)
            for line in lines:
                remain_amount = line.amount - line.paid_amount
                if remain_amount > amount:
                    line.paid_amount += amount
                    break
                elif remain_amount == amount:
                    line.paid_amount += amount
                    line.paid = True
                    break
                else:
                    line.paid_amount += remain_amount
                    amount -= remain_amount
        self.loan_id._compute_loan_amount()
        return True
