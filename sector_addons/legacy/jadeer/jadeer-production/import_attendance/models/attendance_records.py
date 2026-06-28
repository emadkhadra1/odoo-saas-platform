# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

DEFAULT_DATE_FORMAT = '%d/%m/%Y'
DEFAULT_TIME_FORMAT = '%H:%M'


class SelectedAttendanceRecords(models.Model):
    _name = 'attendance.records'
    _rec_name = 'name'

    name = fields.Char(string="Sheet Name", required=True, )
    attendance_record_ids = fields.One2many(comodel_name="attendance.records.lines",
                                            inverse_name="attendance_record_id", )
    date_format = fields.Char(string='Date Format', required=True, default=DEFAULT_DATE_FORMAT)
    time_format = fields.Char(string='Time Format', required=True, default=DEFAULT_TIME_FORMAT)

    @api.constrains('attendance_record_ids', 'attendance_record_ids.column')
    def check_repeated_selection_lines(self):
        selected_columns = self.attendance_record_ids.mapped('column')
        unique_selected_columns = list(set(self.attendance_record_ids.mapped('column')))
        if len(selected_columns) > len(unique_selected_columns):
            raise ValidationError(_('Selected Columns must be unique'))
