# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('unique_attendance_code', 'UNIQUE(attendance_code)', 'Employee Code must be unique')
    ]

    attendance_code = fields.Char(string="Attendance Code", )
