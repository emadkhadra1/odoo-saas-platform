import random
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC
import pytz
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import base64




class EmpPortalloan(models.Model):
    _inherit = "hr.loan"
    @api.model
    def create_loan_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        # if not (values['description'] and values['loan_type'] and values['from'] and values['to']):
        #     return {
        #         'errors': _('All fields are required !')
        #     }
        date = False
        payment_date = False
        date_str = str(values['loan_date'])
        payment_date_str = str(values['payment_date'])
        if values['loan_date']:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        if values['payment_date']:
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d")
        values = {
            'employee_id':   user.employee_id.id,
            'department_id':   user.employee_id.department_id.id,
            'loan_type_id': int(values['loan_type']),
            'loan_amount': values['loan_amount'],
            'installment': values['installments'],
            # 'state': values['state'],
            'date': date,
            'payment_date': payment_date,
        }
        tmp_loan = self.env['hr.loan'].sudo().new(values)
        myloan = self.env['hr.loan'].sudo().create(values)
        return {
            'id': myloan.id
        }
