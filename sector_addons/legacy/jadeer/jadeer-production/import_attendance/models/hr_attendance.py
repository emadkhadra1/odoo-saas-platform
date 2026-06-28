# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    date_day = fields.Date()

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
       pass