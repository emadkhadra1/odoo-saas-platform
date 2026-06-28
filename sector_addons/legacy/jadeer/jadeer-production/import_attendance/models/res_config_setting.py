# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    attendance_records_id = fields.Many2one('attendance.records', string='Attendance Import Sequences')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance_records_id = fields.Many2one('attendance.records', string='Attendance Import Sequences',
                                         related="company_id.attendance_records_id", store=True,
                                         readonly=False)
