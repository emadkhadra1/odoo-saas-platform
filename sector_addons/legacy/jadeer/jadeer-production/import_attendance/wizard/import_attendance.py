# -*- coding: utf-8 -*-
import tempfile
import binascii
import xlrd
import logging
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _
from pytz import timezone, utc
# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    from io import StringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportAttendance(models.Model):
    _name = "import.attendance"
    _rec_name = 'name'

    state = fields.Selection(string="", selection=[
        ('draft', 'Draft'),
        ('imported', 'Imported'),
    ], required=False, default='draft')
    file_name = fields.Char()
    file = fields.Binary(string='Import XLS File')
    result_ids = fields.One2many(comodel_name="import.attendance.result", inverse_name="request_id")
    error_ids = fields.One2many(comodel_name="import.attendance.error", inverse_name="request_id")
    name = fields.Char(string="Name", required=True, )
    attendance_ids = fields.Many2many(comodel_name="hr.attendance", string="Attendance", )
    attendance_count = fields.Integer(string="", compute="calc_attendance_count", store=True)
    date_from = fields.Date(string="", required=True, )
    date_to = fields.Date(string="", required=True, )

    @api.depends('attendance_ids')
    def calc_attendance_count(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids.ids)

    def create_attendance(self, values):
        self.ensure_one()
        attendances = self.env['hr.attendance']

        emp_attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', values.get("employee_id")),
            ('date_day', '=', values.get("date_day")),
            ('check_out', '!=', False),
        ], limit=1)

        if not emp_attendance:
            attendances.create(values)
        else:
            raise ValidationError(
                _("Employee '%s' has already logged at the day of '%s'. ") % (
                    emp_attendance.employee_id.name, values.get("date_day")))

    def import_attendance(self):
        self.ensure_one()
        if not self.file:
            raise ValidationError('You Must Upload Attendance Sheet !!')
        attend_seq = self.env.user.company_id.attendance_records_id
        _logger.info("KKKKKKKKKKKKK{}".format(attend_seq))
        if attend_seq:
            if attend_seq.date_format and attend_seq.time_format:
                date_format = attend_seq.date_format
                time_format = attend_seq.time_format
                date_time_format = date_format + " " + time_format
            else:
                date_time_format = "%Y-%m-%d %H:%M"
            attend_seq_sort = attend_seq.attendance_record_ids.sorted(key=lambda r: r.sequence)
            code = (attend_seq_sort.filtered(lambda r: r.column == 'employee_code')).sequence
            tm = (attend_seq_sort.filtered(lambda r: r.column == 'time')).sequence
            status = (attend_seq_sort.filtered(lambda r: r.column == 'state')).sequence
            new_state = (attend_seq_sort.filtered(lambda r: r.column == 'new_state')).sequence
            exception = (attend_seq_sort.filtered(lambda r: r.column == 'exception')).sequence

            fx = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fx.write(binascii.a2b_base64(self.file))
            fx.seek(0)
            workbook = xlrd.open_workbook(fx.name)
            sheet = workbook.sheet_by_index(0)
            result_dic = {}
            errors = []
            resource_id = None
            attendances = self.env['hr.attendance']
            employee_list = []
            date_from = datetime.combine(self.date_from, time.min)
            date_to = datetime.combine(self.date_to, time.max)
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    field = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    attendance_line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                    if attendance_line[exception] in ['Repeat', 'Invalid']:
                        continue
                    else:
                        emp = self.env['hr.employee'].search(
                            [('attendance_code', '=', int(float(attendance_line[code])))])
                        _logger.info("JJJ{}".format(emp))
                        _logger.info("code{}".format(int(float(attendance_line[code]))))
                        if attendance_line[code] not in employee_list:
                            employee_list.append(attendance_line[code])
                            res = self.env['hr.attendance'].search([
                                ('employee_id', '=', emp.id),
                                ('check_in', '>=', date_from),
                                ('check_in', '<=', date_to),
                            ])
                            res.sudo().unlink()
                        check_date_time = datetime.strptime(str(attendance_line[tm][:-3]), date_time_format)
                        check_date = check_date_time.date()
                        day_night = str(attendance_line[tm][-3:])
                        if 'PM' in day_night and check_date_time.hour != 12:
                            check_date_time = check_date_time + timedelta(hours=12)
                        check_date_time = timezone(self.env.context['tz']).localize(
                            fields.Datetime.from_string(check_date_time), is_dst=None).astimezone(utc)
                        check_date_time = check_date_time.replace(tzinfo=None)
                        string_dt = str(check_date)
                        if emp:
                            # group_id = emp.group_id
                            if attend_seq_sort.filtered(lambda r: r.column == 'new_state'):
                                if attendance_line[new_state]:
                                    state = attendance_line[new_state]
                                else:
                                    state = attendance_line[status]
                            else:
                                state = attendance_line[status]
                            _logger.info("MMMMMMMM{}".format(state))

                            if state == 'C/In':
                                # if group_id:
                                resource_id = emp.resource_calendar_id
                                s_date = datetime.combine(check_date, time.min)
                                e_date = datetime.combine(check_date, time.max)
                                attendance_ids = self.env['hr.attendance'].search([
                                    ('employee_id', '=', emp.id),
                                    ('check_in', '>=', s_date),
                                    ('check_in', '<=', e_date),
                                ])
                                _logger.info("YYYYYYYYYY{}".format(attendance_ids))
                                if attendance_ids:
                                    att_id = self.calc_min_check_in(attendance_ids)
                                    att_id.write({
                                        'check_in': check_date_time,
                                        'date_day': string_dt,
                                    })
                                    result_dic.update({
                                        emp.id: result_dic.get(emp.id) + 1 if result_dic.get(emp.id) else 1
                                    })
                                else:
                                    values = {
                                        'employee_id': emp.id,
                                        'check_in': check_date_time,
                                        'date_day': string_dt,
                                    }
                                    attendances |= self.env['hr.attendance'].create(values)
                                    result_dic.update({
                                        emp.id: result_dic.get(emp.id) + 1 if result_dic.get(emp.id) else 1
                                    })
                            elif state == 'C/Out':
                                if resource_id:
                                    if resource_id.shift_type == 'one':
                                        start_date = datetime.combine(check_date, time.min)
                                        end_date = datetime.combine(check_date, time.max)
                                    else:
                                        dt = check_date + timedelta(days=-1)
                                        start_date = datetime.combine(dt, time.min)
                                        end_date = datetime.combine(dt, time.max)
                                    attend_list = self.env['hr.attendance'].search([
                                        ('employee_id', '=', emp.id),
                                        ('check_in', '>=', start_date),
                                        ('check_in', '<=', end_date),
                                    ])
                                    _logger.info("YYYYYYYYYY{}".format(attendance_ids))

                                    if attend_list:
                                        attend_id = self.calc_max_check_out(attend_list)
                                        attend_id.write({
                                            'check_out': check_date_time
                                        })
                                else:
                                    start_date = datetime.combine(check_date, time.min)
                                    end_date = datetime.combine(check_date, time.max)
                                    attend_list = self.env['hr.attendance'].search([
                                        ('employee_id', '=', emp.id),
                                        ('check_in', '>=', start_date),
                                        ('check_in', '<=', end_date),
                                    ])
                                    if attend_list:
                                        attend_id = self.calc_max_check_out(attend_list)
                                        attend_id.write({
                                            'check_out': check_date_time
                                        })
                                    else:
                                        dt = check_date + timedelta(days=-1)
                                        start_date = datetime.combine(dt, time.min)
                                        end_date = datetime.combine(dt, time.max)
                                        attend_list = self.env['hr.attendance'].search([
                                            ('employee_id', '=', emp.id),
                                            ('check_in', '>=', start_date),
                                            ('check_in', '<=', end_date),
                                        ])
                                        if attend_list:
                                            attend_id = self.calc_max_check_out(attend_list)
                                            attend_id.write({
                                                'check_out': check_date_time
                                            })
                        else:
                            errors.append(attendance_line[code])
        else:
            raise ValidationError('Please Configure Attendance Sheet Columns In settings !')
        self.result_ids.unlink()
        self.error_ids.unlink()
        res_vals = []
        for key, value in result_dic.items():
            res_vals.append({
                'employee_id': key,
                'imported_lines': value,
                'request_id': self.id,
            })
        error_vals = []
        for err in errors:
            error_vals.append({
                'code': err.split('.')[0] if err.split('.') else err,
                'request_id': self.id,
            })
        self.env['import.attendance.result'].create(res_vals)
        self.env['import.attendance.error'].create(error_vals)
        new_attendance = self.attendance_ids + attendances
        self.attendance_ids = new_attendance.ids
        self.state = 'imported'

    def calc_max_check_out(self, attend_list):
        if len(attend_list) > 1:
            max_check_out = max(attend_list.mapped('check_out'))
            res = attend_list.filtered(lambda at: at.check_out == max_check_out)
            return res
        else:
            return attend_list

    def calc_min_check_in(self, attend_list):
        if len(attend_list) > 1:
            min_check_in = min(attend_list.mapped('check_in'))
            res = attend_list.filtered(lambda at: at.check_in == min_check_in)
            return res
        else:
            return attend_list

    def action_draft(self):
        self.state = 'draft'

    def action_close(self):
        self.state = 'imported'


class ImportAttendanceResult(models.Model):
    _name = "import.attendance.result"

    request_id = fields.Many2one(comodel_name="import.attendance", string="Request", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    imported_lines = fields.Integer(string="Imported Lines", required=False, )


class ImportAttendanceError(models.Model):
    _name = "import.attendance.error"

    request_id = fields.Many2one(comodel_name="import.attendance", string="Request", required=False, )
    code = fields.Char(string="Employee Code ", required=False, )
