# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2many('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        super(HrPayslip, self)._onchange_employee()
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        payslip_input_type_id = self.env.ref('ohrms_loan.hr_payslip_input_type_loan')
        if date_from and date_to and employee and payslip_input_type_id:
            lon_obj = self.env['hr.loan'].search([('employee_id', '=', employee.id), ('state', '=', 'approve')])
            total_loan = 0.0
            lst_loans = []
            for loan in lon_obj:
                for loan_line in loan.loan_lines:
                    if date_from <= loan_line.date <= date_to and not loan_line.paid:
                        total_loan += loan_line.amount
                        lst_loans.append((6, 0, loan_line.ids))
            updated = False
            x = lst_loans
            if self.input_line_ids:
                for input_line in self.input_line_ids:
                    if payslip_input_type_id == input_line.input_type_id:
                        input_line.amount = total_loan
                        input_line.loan_line_id = lst_loans
                        updated = True
            if not updated:
                self.input_line_ids = [(0, 0, {
                    'input_type_id': payslip_input_type_id.id,
                    'loan_line_id': lst_loans,
                    'amount': total_loan,
                })]
    #
    # def action_payslip_done(self):
    #     for line in self.input_line_ids:
    #         if line.loan_line_id:
    #             line.loan_line_id.paid = True
    #             line.loan_line_id.loan_id._compute_loan_amount()
    #     return super(HrPayslip, self).action_payslip_done()
