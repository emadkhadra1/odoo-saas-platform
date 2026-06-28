# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class Loan(models.Model):
    _inherit = 'hr.loan'

    is_rescheduled = fields.Boolean(string="IS Rescheduled ?", )
    loan_type_id = fields.Many2one(comodel_name="loan.type")

    @api.constrains('loan_amount','employee_id.contract_id.basic_salary','loan_type_id.factor')
    def check_loan_type(self):
        if self.loan_amount > (self.employee_id.contract_id.basic_salary * self.loan_type_id.factor) :
            raise ValidationError("Exceed Loan Type Amount !")


class LoanLine(models.Model):
    _inherit = 'hr.loan.line'

    def action_installment_reschedule(self):
        if self.paid:
            raise exceptions.ValidationError('Can not reschedule paid installment !')
        view = self.env.ref('ohrms_loan.loan_line_wizard')
        return {
            'name': _('Installment Reschedule'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'loan.line.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_old_amount': self.amount,
                'default_new_date': self.date,
                'default_amount': self.amount,
                'default_loan_line_id': self.id,
                'default_loan_id': self.loan_id.id
            }
        }
