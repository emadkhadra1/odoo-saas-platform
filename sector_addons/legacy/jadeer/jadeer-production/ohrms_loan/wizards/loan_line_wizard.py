# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError, Warning
from dateutil.relativedelta import relativedelta



class LoanLineWizard(models.TransientModel):
    _name = 'loan.line.wizard'
    _rec_name = 'amount'
    _description = 'Loan Line Details'

    amount = fields.Float(string="Updated Amount", required=True, )
    old_amount = fields.Float(string="Old Amount", )
    loan_line_id = fields.Many2one(comodel_name="hr.loan.line")
    loan_id = fields.Many2one(comodel_name="hr.loan")
    new_date = fields.Date(string="Date")
    is_last_installment = fields.Boolean(related="loan_line_id.is_last_installment")
    update_type = fields.Selection(string="Update Type", selection=[('amount', 'Amount'), ('date', 'Date'), ],
                                   required=True, default='amount')

    def update_amount(self):
        diff = self.old_amount - self.amount
        index = 0
        for line in self.loan_id.loan_lines:
            index += 1
            if line == self.loan_line_id:
                line.amount = self.amount
                break
        try:
            line_diff = diff / (len(self.loan_id.loan_lines) - index)
            for i, line_loan in enumerate(self.loan_id.loan_lines):
                if i >= index:
                    line_loan.amount += line_diff
        except:
            raise ValidationError("Last Installment ! You Can Change The Payment Date")

    def update_date(self):
        if self.loan_line_id.date != self.new_date:
            for line in self.loan_id.loan_lines.filtered(lambda x: x.date > self.loan_line_id.date):
                line.date = line.date + relativedelta(months=1)
            self.loan_line_id.date = self.new_date
            self.loan_id.is_rescheduled = True

