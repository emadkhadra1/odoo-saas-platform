# See LICENSE file for full copyright and licensing details.

import random
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC
import pytz
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import base64




class EmpPortalTimeOff(models.Model):
    _inherit = "hr.leave"

    def update_timeoff_portal(self, values):
        dt_from = values['from']
        dt_to = values['to']
        if dt_from:
            dt_from = datetime.strptime(dt_from, DF).date()
        if dt_to:
            dt_to = datetime.strptime(dt_to, DF).date()
        date_from_time_str = str(dt_from)+' '+values['request_hour_from']
        date_to_time_str = str(dt_to)+' '+values['request_hour_to']
        date_from = False
        date_to = False
        if values['request_hour_to'] and values['request_hour_from']:
            date_from = datetime.strptime(date_from_time_str, "%Y-%m-%d %H:%M")- timedelta(hours=2)
            date_to = datetime.strptime(date_to_time_str, "%Y-%m-%d %H:%M") - timedelta(hours=2)
        for timeoff in self:
            timeoff_values = {
                'name': values['description'],
                'holiday_status_id': int(values['timeoff_type']),
                'request_date_from': dt_from,
                'request_date_to': dt_to,
                'request_unit_half': values['half_day'],
                'request_unit_hours': values['custom_hours'],
                'request_hour_from': date_from,
                'request_hour_to': date_to,

                'request_date_from_period': values['request_date_from_period'],
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._compute_date_from_to()
        return True

    @api.model
    def create_timeoff_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        # if not (values['description'] and values['timeoff_type'] and values['from'] and values['to']):
        #     return {
        #         'errors': _('All fields are required !')
        #     }
        date_from = False
        date_to = False
        date_from_time_str = str(values['from'])+' '+values['request_hour_from']
        date_to_time_str = str(values['to'])+' '+values['request_hour_to']
        if values['request_hour_to'] and values['request_hour_from'] :
            date_from = datetime.strptime(date_from_time_str, "%Y-%m-%d %H:%M")- timedelta(hours=2)
            date_to = datetime.strptime(date_to_time_str, "%Y-%m-%d %H:%M") - timedelta(hours=2)
        values = {
            'name': values['description'],
            # 'employee_ids':  [(4, 0, 5)],
            'employee_id':   user.employee_id.id,
            'holiday_status_id': int(values['timeoff_type']),
            'request_date_from': values['from'],
            'request_date_to': values['to'],
            'request_unit_half': values['half_day'],
            'request_unit_hours': values['custom_hours'],
            'request_hour_from': date_from,
            'request_hour_to': date_to,

            'request_date_from_period': values['request_date_from_period'],
        }
        tmp_leave = self.env['hr.leave'].sudo().new(values)
        tmp_leave._compute_date_from_to()
        values = tmp_leave._convert_to_write(tmp_leave._cache)
        mytimeoff = self.env['hr.leave'].sudo().create(values)
        return {
            'id': mytimeoff.id
        }
class EmpPortalAllocations(models.Model):
    _inherit = "hr.leave.allocation"
    @api.model
    def create_allocation_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        # if not (values['description'] and values['loan_type'] and values['from'] and values['to']):
        #     return {
        #         'errors': _('All fields are required !')
        #     }
        date_from = False
        date_to = False
        duration = 0
        date_from_str = str(values['allocation_date'])
        date_to_str = str(values['allocation_date_to'])
        if values['allocation_date']:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
        if values['allocation_date_to']:
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d")

        holidays_status = self.env['hr.leave.type'].search([('id','=',int(values['holiday_status_id']))],limit=1)
        if holidays_status.request_unit == 'day':
           duration= int(values['duration'])
        elif holidays_status.request_unit == 'hour':
           duration= int(values['duration'])/8
        values = {
            'name' : str(values['description']),
            'employee_id':   user.employee_id.id,
            'holiday_status_id': int(values['holiday_status_id']),
            # 'state': values['state'],
            'date_from': date_from,
            'date_to': date_to,
            'number_of_days': duration,
        }
        myloan = self.env['hr.leave.allocation'].sudo().create(values)
        return {
            'id': myloan.id
        }
