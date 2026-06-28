# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class SelectedAttendanceRecordsLines(models.Model):
    _name = 'attendance.records.lines'

    column = fields.Selection(string="Column",
                              selection=[('employee_code', 'Employee Code'), ('time', 'Time'), ('state', 'State'),
                                         ('new_state', 'New State'), ('exception', 'Exception'), ],
                              required=True, )
    sequence = fields.Integer(string="sequence", required=True, )
    attendance_record_id = fields.Many2one(comodel_name="attendance.records", )
