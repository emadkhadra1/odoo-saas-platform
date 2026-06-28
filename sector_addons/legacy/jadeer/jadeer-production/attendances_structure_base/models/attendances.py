import math
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
from odoo.fields import Date, Datetime
# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class EmployeeAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['hr.attendance', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']

    pin = fields.Char(related="employee_id.pin")
    late = fields.Float(string='Late', compute='_compute_late_hours', store=True)
    over_time = fields.Float(string='Over Time')
    early = fields.Float(string='Early Leave', compute='_compute_early_leave_hours', store=True)
    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        default=lambda self: self._context.get('tz') or self.env.user.tz,
        help="This field is used in order to define in which timezone the resources will work.")
    resource_id = fields.Many2one(comodel_name="resource.calendar", string="Working Times", required=False, )
    overtime_type = fields.Selection(string="Overtime Type", selection=[
        ('public_holiday', 'Public Holiday'),
        ('weekly_holiday', 'Weekly Holiday'),
        ('work_day', 'Work Day'),
    ], required=False)
    is_flixable = fields.Boolean()


    # TODO: Function commented to handle ZK attendance import
    # @api.constrains('check_in', 'check_out', 'employee_id')
    # def _check_validity(self):
    #     """ Verifies the validity of the attendance record compared to the others from the same employee.
    #         For the same employee we must have :
    #             * maximum 1 "open" attendance record (without check_out)
    #             * no overlapping time slices with previous employee records
    #     """
    #     for attendance in self:
    #         # we take the latest attendance before our check_in time and check it doesn't overlap with ours
    #         last_attendance_before_check_in = self.env['hr.attendance'].search([
    #             ('employee_id', '=', attendance.employee_id.id),
    #             ('check_in', '<=', attendance.check_in),
    #             ('id', '!=', attendance.id),
    #         ], order='check_in desc', limit=1)
    #         if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
    #             raise exceptions.ValidationError(_(
    #                 "Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
    #                                                  'empl_name': attendance.employee_id.name,
    #                                                  'datetime': fields.Datetime.to_string(
    #                                                      fields.Datetime.context_timestamp(self,
    #                                                                                        fields.Datetime.from_string(
    #                                                                                            attendance.check_in))),
    #                                              })
    #
    #         # if not attendance.check_out:
    #         #     pass
    #         # else:
    #         #     # we verify that the latest attendance with check_in time before our check_out time
    #         #     # is the same as the one before our check_in time computed before, otherwise it overlaps
    #         #     last_attendance_before_check_out = self.env['hr.attendance'].search([
    #         #         ('employee_id', '=', attendance.employee_id.id),
    #         #         ('check_in', '<', attendance.check_out),
    #         #         ('id', '!=', attendance.id),
    #         #     ], order='check_in desc', limit=1)
    #         #     if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
    #         #         raise exceptions.ValidationError(_(
    #         #             "Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
    #         #                                              'empl_name': attendance.employee_id.name,
    #         #                                              'datetime': fields.Datetime.to_string(
    #         #                                                  fields.Datetime.context_timestamp(self,
    #         #                                                                                    fields.Datetime.from_string(
    #         #                                                                                        last_attendance_before_check_out.check_in))),
    #         #                                          })

    def get_check_in_day(self, attendance):
        for attend in attendance:
            if attend.check_in:
                day = attend.check_in.weekday()
                return day

    def get_resource_calender(self, group_id, date):
        if group_id:
            resource_id = self.env['hr.employee.group.line'].search([
                ('group_id', '=', group_id.id),
                ('date_from', '<=', date),
                ('date_to', '>=', date),
            ], limit=1)
            if not resource_id:
                return None
            return resource_id.shift_id
        else:
            return None

    def is_same_working_day(self, resource_id):
        check_in_day = self.get_check_in_day(self)
        res = self.env['resource.calendar.attendance'].search([
            ('calendar_id', '=', resource_id.id),
            ('dayofweek', '=', check_in_day)
        ])
        if res:
            return True
        return False

    def is_public_holidays_day(self, resource_id, dt):
        work_from = self.env['resource.calendar.leaves'].search([
            ('calendar_id', '=', resource_id.id),
            ('resource_id', '=', False),
            ('date_from', '<=', dt),
            ('date_to', '>=', dt)
        ])
        if work_from:
            return True
        return False

    def check_has_leave(self):
        res = self.env['hr.leave'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', self.check_in),
            ('date_to', '>=', self.check_in),
        ])
        return res

    def get_working_from(self, resource_id):
        day = self.check_in.weekday()
        work_from = self.env['resource.calendar.attendance'].search([
            ('calendar_id', '=', resource_id.id),
            ('dayofweek', '=', day),
            ('shift_start', '=', True),
        ], limit=1).hour_from
        return work_from

    def get_working_to(self, resource_id):
        day = self.check_in.weekday()
        work_to = self.env['resource.calendar.attendance'].search([
            ('calendar_id', '=', resource_id.id),
            ('dayofweek', '=', day),
        ])
        if len(work_to) > 1:
            res = work_to.filtered(lambda l: not l.shift_start)
            return res[0].hour_to
        else:
            return work_to.hour_to

    def apply_penalty(self, structure_id, late_time, rule_type):
        rule = self.env['attendance.deduction.rules']
        if rule_type == 'late':
            rules = structure_id.structure_ids.filtered(lambda l: l.duration_type == 'late')
            rule |= self.get_attendance_rule(rules, late_time)
        elif rule_type == 'early':
            rules = structure_id.structure_ids.filtered(lambda l: l.duration_type == 'early')
            rule |= self.get_attendance_rule(rules, late_time)

        return rule

    def get_attendance_rule(self, rules, actual_date):
        rule = self.env['attendance.deduction.rules']
        for line in rules:
            from_time = line.from_time
            to_time = line.to_time
            if line.remaining:
                rule |= line
                break
            elif from_time <= actual_date <= to_time:
                rule |= line
                break
        return rule

    @api.depends('check_in', 'employee_id')
    def _compute_late_hours(self):
        for attendance in self:
            dt = attendance.check_in.date()
            resource_id = attendance.employee_id.resource_calendar_id
            if not resource_id:
                attendance.late = 0
                continue
            public_holidays = attendance.is_public_holidays_day(resource_id, dt)
            working_day = attendance.is_same_working_day(resource_id)
            has_leave = attendance.check_has_leave()
            if attendance.check_in and working_day and not public_holidays and not has_leave:
                planned_check_in = attendance.get_working_from(resource_id)
                check_in = Datetime.context_timestamp(attendance, Datetime.from_string(attendance.check_in))
                check_in_time = check_in.time()
                actual_check_in = check_in_time.hour + (check_in_time.minute / 60) + (
                        check_in_time.second / (60 * 60))
                if actual_check_in < planned_check_in:
                    attendance.late = 0
                    continue
                attendance.late = actual_check_in - planned_check_in

            else:
                attendance.late = 0

    @api.depends('check_out', 'employee_id')
    def _compute_early_leave_hours(self):
        for attendance in self:
            dt = attendance.check_in.date()
            resource_id = attendance.employee_id.resource_calendar_id
            if not resource_id:
                attendance.early = 0
                continue
            public_holidays = attendance.is_public_holidays_day(resource_id, dt)
            working_day = attendance.is_same_working_day(resource_id)
            has_leave = attendance.check_has_leave()
            if attendance.check_out and working_day and not public_holidays and not has_leave:
                planned_check_out = attendance.get_working_to(resource_id)
                check_out = Datetime.context_timestamp(attendance, Datetime.from_string(attendance.check_out))
                check_out_time = check_out.time()
                actual_check_out = check_out_time.hour + (check_out_time.minute / 60) + (
                        check_out_time.second / (60 * 60))
                if actual_check_out > planned_check_out:
                    attendance.early = 0
                    continue
                attendance.early = planned_check_out - actual_check_out
            else:
                attendance.early = 0

    @api.constrains('check_out')
    def over_time_calculate(self):
        for rec in self:
            if rec.check_out:
                dt = rec.check_out.date()
                resource_id = rec.employee_id.resource_calendar_id
                if not resource_id:
                    continue
                overtime_start_limit = resource_id.attendance_id.overtime_start_limit
                public_holidays = rec.is_public_holidays_day(resource_id, dt)
                if public_holidays:
                    if overtime_start_limit > 0.0:
                        if rec.worked_hours >= overtime_start_limit:
                            rec.over_time = rec.worked_hours
                            rec.overtime_type = 'public_holiday'
                    else:
                        if rec.worked_hours > 0.0:
                            rec.over_time = rec.worked_hours
                            rec.overtime_type = 'public_holiday'
                    continue

                working_day = rec.is_same_working_day(resource_id)
                if working_day:
                    if resource_id:
                        hours_per_day = resource_id.hours_per_day
                        overtime = rec.worked_hours - hours_per_day
                        if overtime_start_limit > 0.0:
                            if overtime >= overtime_start_limit:
                                rec.over_time = overtime
                                rec.overtime_type = 'work_day'
                            else:
                                rec.over_time = 0
                                rec.overtime_type = False
                        else:
                            if overtime >= 0.0:
                                rec.over_time = overtime
                                rec.overtime_type = 'work_day'
                            else:
                                rec.over_time = 0
                                rec.overtime_type = False
                    else:
                        if overtime_start_limit > 0.0:
                            if rec.worked_hours >= overtime_start_limit:
                                rec.over_time = rec.worked_hours
                                rec.overtime_type = 'weekly_holiday'
                        else:
                            if rec.worked_hours > 0.0:
                                rec.over_time = rec.worked_hours
                                rec.overtime_type = 'weekly_holiday'
                        continue
                else:
                    if overtime_start_limit > 0.0:
                        if rec.worked_hours >= overtime_start_limit:
                            rec.over_time = rec.worked_hours
                            rec.overtime_type = 'weekly_holiday'
                    else:
                        if rec.worked_hours > 0.0:
                            rec.over_time = rec.worked_hours
                            rec.overtime_type = 'weekly_holiday'
                    continue

    def apply_overtime(self, resource_id):
        pass

    def day_name(self, name):
        if name == "Monday":
            return 0
        elif name == "Tuesday":
            return 1
        elif name == "Wednesday":
            return 2
        elif name == "Thursday":
            return 3
        elif name == "Friday":
            return 4
        elif name == "Saturday":
            return 5
        elif name == "Sunday":
            return 6
        else:
            return 0000


class Employee_inh(models.Model):
    _inherit = 'hr.employee'

    attendance_rule = fields.Many2one('attendance.structure', string='Attendance Rule')
