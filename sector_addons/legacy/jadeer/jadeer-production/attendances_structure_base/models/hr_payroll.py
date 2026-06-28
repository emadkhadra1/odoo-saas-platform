from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
import pandas as pd

DAYS = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6,
}


class HrPayrollRule(models.Model):
    _name = 'hr.payslip.attendance'
    _rec_name = 'name'

    name = fields.Char('Description')
    date = fields.Date(string="Day", required=False, )
    hours = fields.Float(string="Hours", required=False, )
    apply_hours = fields.Float(string="Applied Hours", required=False, )
    rule_id = fields.Many2one(comodel_name="hr.payslip", string="Payslip", required=False)
    employee_id = fields.Many2one(
        'hr.employee',
    )


class hr_payroll(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'date_from', 'date_to')
    def calc_employee_attendance(self):
        for line in self:
            emp_attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', line.employee_id.id),
                ('check_in', '>=', line.date_from),
                ('check_in', '<=', line.date_to),
            ])
            line.hr_attendance_ids = emp_attendances.ids

    def get_employee_attendance(self):
        emp_attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', self.date_from),
            ('check_in', '<=', self.date_to),
        ])
        return emp_attendances

    attend_rule_ids = fields.One2many(comodel_name="hr.payslip.attendance",
                                      string="Attendance Rules",
                                      inverse_name='rule_id', )
    deduction_amount = fields.Float(string="Deduction Amount", compute='_compute_penalty')
    work_day_over_time = fields.Float(string='Work Day Over Time', compute='_compute_penalty')
    work_night_over_time = fields.Float(string='Work Night Over Time', compute='_compute_penalty')
    weekly_leave_over_time = fields.Float(string='Weekly Leave Over Time', compute='_compute_penalty')
    public_leave_over_time = fields.Float(string='Public Leave Over Time', compute='_compute_penalty')
    absent_amount = fields.Float(string="Absent Amount", compute='_compute_penalty')
    no_checkout_amount = fields.Float(string="No Checkout Amount", compute='_compute_penalty')
    not_in_contract_amount = fields.Float(string="Not In Contract Amount", compute='_compute_not_in_contracts')
    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        default=lambda self: self._context.get('tz') or self.env.user.tz or 'UTC',
        help="This field is used in order to define in which timezone the resources will work.")
    hr_attendance_ids = fields.Many2many(comodel_name="hr.attendance", string="Actual Attendance",
                                         compute="calc_employee_attendance",
                                         store=True)

    def get_hour_value(self):
        wage = self.contract_id.wage
        no_month_days = self.company_id.no_month_days
        day_value = wage / (no_month_days or 30)
        hours_per_day = self.employee_id.resource_calendar_id.hours_per_day
        hour_value = day_value / (hours_per_day or 8)
        return hour_value

    def get_day_value(self):
        wage = self.contract_id.wage
        no_month_days = self.company_id.no_month_days
        day_value = wage / (no_month_days or 30)
        return day_value

    @api.depends('contract_id', 'employee_id')
    def _compute_not_in_contracts(self):
        for record in self:
            # hour_value = record.get_hour_value()
            day_value = record.get_day_value()
            start_date = record.date_from
            end_date = record.date_to
            not_in_contract_amount = 0.0
            contract = record.contract_id
            if contract:
                for single_date in pd.date_range(start_date, end_date):
                    if contract.date_end:
                        if not contract.date_start <= single_date.date() <= contract.date_end:
                            not_in_contract_amount += day_value
                    else:
                        if not contract.date_start <= single_date.date():
                            not_in_contract_amount += day_value
                record.not_in_contract_amount = not_in_contract_amount
            else:
                record.not_in_contract_amount = 0



    @api.depends('attend_rule_ids')
    def _compute_penalty(self):
        for record in self:
            contract_id = record.contract_id
            if contract_id:
                hour_value = contract_id.hour_value
                work_day_rate = 1
                work_night_rate = 1
                public_leave_rate = 1
                weekly_leave_rate = 1
                attendance_structure_id = record.employee_id.resource_calendar_id.attendance_id
                if attendance_structure_id:
                    work_day_rate = attendance_structure_id.work_day_rate
                    work_night_rate = attendance_structure_id.work_night_rate
                    public_leave_rate = attendance_structure_id.public_leave_rate
                    weekly_leave_rate = attendance_structure_id.weekly_leave_rate
                late_amount = 0.0
                absent_amount = 0.0
                no_checkout_amount = 0.0
                work_day_overtime = 0.0
                work_night_overtime = 0.0
                public_holiday_overtime = 0.0
                weekly_leave_over_time = 0.0
                if record.attend_rule_ids:
                    for line in record.attend_rule_ids:
                        if line.name in ['Late Check in', 'Early Check Out']:
                            late_amount += line.apply_hours * hour_value
                        elif line.name == 'Absent':
                            absent_amount += line.apply_hours * hour_value
                        elif line.name == 'No Checkout':
                            no_checkout_amount += line.apply_hours * hour_value
                        elif line.name == 'Work Day Over Time':
                            work_day_overtime += (line.hours * work_day_rate) * hour_value
                        elif line.name == 'Work Night Over Time':
                            work_night_overtime += (line.hours * work_night_rate) * hour_value
                        elif line.name == 'Public Holiday Over Time':
                            public_holiday_overtime += (line.hours * public_leave_rate) * hour_value
                        elif line.name == 'Weekly Holiday Over Time':
                            weekly_leave_over_time += (line.hours * weekly_leave_rate) * hour_value
                    record.deduction_amount = late_amount
                    record.absent_amount = absent_amount
                    record.no_checkout_amount = no_checkout_amount
                    record.work_day_over_time = work_day_overtime
                    record.work_night_over_time = work_night_overtime
                    record.public_leave_over_time = public_holiday_overtime
                    record.weekly_leave_over_time = weekly_leave_over_time
                else:
                    record.deduction_amount = 0.0
                    record.absent_amount = 0.0
                    record.no_checkout_amount = 0.0
                    record.work_day_over_time = 0.0
                    record.work_night_over_time = 0.0
                    record.public_leave_over_time = 0.0
                    record.weekly_leave_over_time = 0.0
            else:
                record.deduction_amount = 0.0
                record.absent_amount = 0.0
                record.no_checkout_amount = 0.0
                record.work_day_over_time = 0.0
                record.work_night_over_time = 0.0
                record.public_leave_over_time = 0.0
                record.weekly_leave_over_time = 0.0

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

    def is_same_working_day(self, resource_id, dt):
        day = self.day_name(datetime.strftime(dt, '%A'))
        res = self.env['resource.calendar.attendance'].search([
            ('calendar_id', '=', resource_id.id),
            ('dayofweek', '=', day)
        ])
        if res:
            return True
        return False

    def is_public_holidays_day(self, resource_id, dt):
        work_from = self.env['resource.calendar.leaves'].search([
            ('calendar_id', '=', resource_id.id),
            ('date_from', '<=', dt),
            ('date_to', '>=', dt)
        ])
        if work_from:
            return True
        return False

    def check_has_leave(self, dt):
        res = self.env['hr.leave'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', dt.date()),
            ('date_to', '>=', dt.date()),
        ])
        return res

    def is_in_contract(self, dt):
        contract = self.employee_id.contract_id
        if contract:
            if contract.date_end:
                if contract.date_start <= dt.date() <= contract.date_end:
                    return True
            else:
                if contract.date_start <= dt.date():
                    return True
        return False

    def get_attendance_absent(self):
        rule_repetition = {}
        for record in self:
            rules = []
            start_date = record.date_from
            end_date = record.date_to
            attendance_list = record.get_employee_attendance()
            for single_date in pd.date_range(start_date, end_date):
                resource_id = record.employee_id.resource_calendar_id
                if not resource_id:
                    continue
                is_same_working_day = record.is_same_working_day(resource_id, single_date)
                is_public_holidays_day = record.is_public_holidays_day(resource_id, single_date)
                is_leave_day = record.check_has_leave(single_date)
                is_in_contract = record.is_in_contract(single_date)
                if is_same_working_day and not is_public_holidays_day and not is_leave_day and is_in_contract:
                    has_attend_record = False
                    for line in attendance_list:
                        if line.check_in and line.check_out:
                            if line.check_in.date() <= single_date.date() <= line.check_out.date():
                                has_attend_record = True
                        elif line.check_in.date() == single_date.date():
                            has_attend_record = True
                    if not has_attend_record:
                        absent_rule = resource_id.attendance_id.structure_ids.filtered(
                            lambda r: r.duration_type == 'absent')
                        if absent_rule:
                            if rule_repetition.get(absent_rule):
                                rule_repetition[absent_rule] = rule_repetition[absent_rule] + 1
                            else:
                                rule_repetition[absent_rule] = 1
                            hours_per_day = resource_id.hours_per_day
                            penalty = absent_rule[0].get_penalty(rule_repetition.get(absent_rule) or 1,
                                                                 hours_per_day)
                            if penalty:
                                hours_per_day = resource_id.hours_per_day
                                rules.append((0, 0, {
                                    'name': 'Absent',
                                    'date': single_date,
                                    'hours': hours_per_day,
                                    'apply_hours': penalty,
                                    'rule_id': record.id,
                                    'employee_id': record.employee_id.id,
                                }))
            if rules:
                record.write({'attend_rule_ids': rules})

    def get_no_checkout(self):
        rule_repetition = {}
        for record in self:
            rules = []
            attendance_list = record.get_employee_attendance()
            for single_date in attendance_list.filtered(lambda at: not at.check_out).mapped('check_in'):
                resource_id = record.employee_id.resource_calendar_id
                if not resource_id:
                    continue
                no_checkout_rule = resource_id.attendance_id.structure_ids.filtered(
                    lambda r: r.duration_type == 'no_check')
                if no_checkout_rule:
                    if rule_repetition.get(no_checkout_rule[0]):
                        rule_repetition[no_checkout_rule[0]] = rule_repetition[no_checkout_rule[0]] + 1
                    else:
                        rule_repetition[no_checkout_rule[0]] = 1
                    hours_per_day = resource_id.hours_per_day
                    penalty = no_checkout_rule[0].get_penalty(rule_repetition.get(no_checkout_rule[0]) or 1,
                                                              hours_per_day)
                    if penalty:
                        hours_per_day = resource_id.hours_per_day
                        rules.append((0, 0, {
                            'name': 'No Checkout',
                            'date': single_date,
                            'hours': hours_per_day,
                            'apply_hours': penalty,
                            'rule_id': record.id,
                            'employee_id': record.employee_id.id,
                        }))
            if rules:
                record.write({'attend_rule_ids': rules})

    def get_late_after_permission(self,late,permission):
        remaining_permission = permission
        if late <= 30 and remaining_permission > late:
            late_after_permission = 0
            remaining_permission -= late
            return late_after_permission , remaining_permission
        elif late > 30 and remaining_permission > late:
            late_after_permission = late - 30
            remaining_permission -= 30
            return  late_after_permission,remaining_permission
        else:
            late_after_permission = late - remaining_permission
            if (remaining_permission - late) > 0:
                remaining_permission -= late
            else:
                remaining_permission = 0
            return late_after_permission,remaining_permission

    def calc_attendance_penalty(self):
        rule_repetition = {}
        for record in self:
            record.attend_rule_ids.unlink()
            rules = []
            resource_id = record.employee_id.resource_calendar_id
            permission = resource_id.attendance_id.permission
            for attendance in record.get_employee_attendance().sorted(key='check_in'):
                if attendance.late:
                    penalty_rule = attendance.apply_penalty(resource_id.attendance_id, attendance.late, 'late')
                    if penalty_rule:
                        if rule_repetition.get(penalty_rule):
                            rule_repetition[penalty_rule] = rule_repetition[penalty_rule] + 1
                        else:
                            rule_repetition[penalty_rule] = 1
                        hours_per_day = 0.0
                        if resource_id:
                            hours_per_day = resource_id.hours_per_day

                        late_after_permission,remain_permission = self.get_late_after_permission(attendance.late,permission)
                        penalty = penalty_rule[0].get_penalty(rule_repetition.get(penalty_rule) or 1, hours_per_day,
                                                              late_after_permission)
                        permission = remain_permission
                        if penalty:
                            rules.append((0, 0, {
                                'name': 'Late Check in',
                                'date': attendance.check_in,
                                'hours': attendance.late,
                                'apply_hours': penalty,
                                'rule_id': record.id,
                                'employee_id': record.employee_id.id,
                            }))
                if attendance.early:
                    penalty_rule = attendance.apply_penalty(resource_id.attendance_id, attendance.early, 'early')
                    if penalty_rule:
                        if rule_repetition.get(penalty_rule):
                            rule_repetition[penalty_rule] = rule_repetition[penalty_rule] + 1
                        else:
                            rule_repetition[penalty_rule] = 1
                        hours_per_day = 0.0
                        if resource_id:
                            hours_per_day = resource_id.hours_per_day
                        penalty = penalty_rule[0].get_penalty(rule_repetition.get(penalty_rule) or 1, hours_per_day,
                                                              attendance.early)
                        if penalty:
                            rules.append((0, 0, {
                                'name': 'Early Check Out',
                                'date': attendance.check_out,
                                'hours': attendance.early,
                                'apply_hours': penalty,
                                'rule_id': record.id,
                                'employee_id': record.employee_id.id,
                            }))
            if rules:
                record.write({'attend_rule_ids': rules})

    def get_attendance_over_time(self):
        for record in self:
            rules = []
            resource_id = record.employee_id.resource_calendar_id
            structure_id = resource_id.attendance_id
            if structure_id:
                use_day_night_overtime = structure_id.use_day_night_overtime
                work_day_rate = structure_id.work_day_rate
                work_night_rate = structure_id.work_night_rate
                public_leave_rate = structure_id.public_leave_rate
                weekly_leave_rate = structure_id.weekly_leave_rate
                overtime_start_limit = structure_id.overtime_start_limit
                overtime_start_night_limit = structure_id.overtime_start_night_limit
                for attendance in record.get_employee_attendance().filtered(lambda l: l.over_time > 0.0):
                    if attendance.overtime_type:
                        if attendance.overtime_type == 'public_holiday':
                            rules.append((0, 0, {
                                'name': 'Public Holiday Over Time',
                                'date': attendance.check_in,
                                'hours': attendance.over_time,
                                'apply_hours': attendance.over_time * public_leave_rate if public_leave_rate else 0.0,
                                'rule_id': record.id,
                                'employee_id': record.employee_id.id,
                            }))
                        elif attendance.overtime_type == 'weekly_holiday':
                            rules.append((0, 0, {
                                'name': 'Weekly Holiday Over Time',
                                'date': attendance.check_in,
                                'hours': attendance.over_time,
                                'apply_hours': attendance.over_time * weekly_leave_rate if weekly_leave_rate else 0.0,
                                'rule_id': record.id,
                                'employee_id': record.employee_id.id,
                            }))
                        elif attendance.overtime_type == 'work_day':
                            overtime = attendance.over_time - overtime_start_limit
                            if use_day_night_overtime:
                                overtime_night = attendance.over_time - overtime_start_night_limit
                                overtime = attendance.over_time - overtime_night - overtime_start_limit
                                if overtime_night < 0:
                                    overtime_night = 0
                            if overtime < 0:
                                overtime = 0
                            rules.append((0, 0, {
                                'name': 'Work Day Over Time',
                                'date': attendance.check_in,
                                'hours': overtime,
                                'apply_hours': overtime * work_day_rate if work_day_rate else 0.0,
                                'rule_id': record.id,
                                'employee_id': record.employee_id.id,
                            }))
                            if use_day_night_overtime:
                                rules.append((0, 0, {
                                    'name': 'Work Night Over Time',
                                    'date': attendance.check_in,
                                    'hours': overtime_night,
                                    'apply_hours': overtime_night * work_night_rate if work_night_rate else 0.0,
                                    'rule_id': record.id,
                                    'employee_id': record.employee_id.id,
                                }))
            if rules:
                record.write({'attend_rule_ids': rules})

    def compute_sheet(self):
        for payslip in self:
            payslip.line_ids.unlink()
            payslip.calc_attendance_penalty()
            payslip.get_attendance_over_time()
            payslip.get_no_checkout()
            payslip.get_attendance_absent()
        res = super(hr_payroll, self).compute_sheet()
        return res
