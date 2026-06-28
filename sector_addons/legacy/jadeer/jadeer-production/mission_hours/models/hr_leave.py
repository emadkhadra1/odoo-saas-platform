# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
import calendar


class Leave(models.Model):
    _inherit = 'hr.leave'

    @api.constrains(
        'holiday_status_id',
        'holiday_status_id.mission_hours',
        'holiday_status_id.occurrence_number',
        'holiday_status_id.min_hour_per_time',
        'holiday_status_id.max_hour_per_time',
        'date_from',
        'date_to',
    )
    def mission_hours_check(self):
        if self.holiday_status_id.mission_hours:
            # return records of leave request in this month
            missions = self.get_previous_mission_hours()
            # return num of hours of leave request in this month
            mission_hour = self.get_previous_mission_total_hours()
            current_mission_hour = self.get_current_mission_hours()
            if current_mission_hour > self.holiday_status_id.max_hour_per_time:
                raise exceptions.ValidationError('You have reached the Hour limit of this type!')
            if mission_hour:
                previous_times = mission_hour
                if previous_times > self.holiday_status_id.occurrence_number:
                    raise exceptions.ValidationError('You have reached the Hour limit of this type this month !')
            if missions:
                previous_times = len(missions)
                if previous_times >= self.holiday_status_id.occurrence_number:
                    raise exceptions.ValidationError('You have reached the limit of this type this month !')
            if self.number_of_hours_display and self.number_of_hours_display < self.holiday_status_id.min_hour_per_time:
                raise exceptions.ValidationError(
                    'Number Of Hours is {} and must be greater than {}'.format(self.number_of_hours_display,
                                                                               self.holiday_status_id.min_hour_per_time))

    def get_previous_mission_total_hours(self):
        start, end = self.get_month_day_range(self.request_date_from)
        start_date = datetime.combine(start, time.min)
        end_date = datetime.combine(end, time.max)
        previous_missions_hours = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('holiday_status_id', '=', self.holiday_status_id.id),
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date),
            ('state', 'in', ['confirm','validate']),
        ]) - self
        hours = 0
        for pre in previous_missions_hours:
            hours += pre.number_of_days * 8
        return hours

    def get_previous_mission_hours(self):
        start, end = self.get_month_day_range(self.request_date_from)
        start_date = datetime.combine(start, time.min)
        end_date = datetime.combine(end, time.max)
        previous_missions = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('holiday_status_id', '=', self.holiday_status_id.id),
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date),
            ('state', 'in', ['confirm','validate']),
        ])
        return previous_missions

    def get_month_day_range(self, date):
        first_day = date.replace(day=1)
        last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])
        return first_day, last_day

    def days_hours_minutes(self, td):
        return td.days, td.seconds // 3600, (td.seconds // 60) % 60

    def get_current_mission_hours(self):
        td = self.date_to - self.date_from
        days, hours, minutes = self.days_hours_minutes(td)
        return hours + minutes / 60
