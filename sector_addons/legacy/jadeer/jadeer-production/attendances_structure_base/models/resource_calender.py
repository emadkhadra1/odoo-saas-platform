# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    shift_type = fields.Selection(string="Shift Type", selection=[
        ('one', 'In One Day'),
        ('two', 'In Two Day'),
    ], required=False, default='one')

    @api.onchange('shift_type')
    def onchange_shift_type(self):
        if self.shift_type == 'one':
            self.attendance_ids.write({
                'shift_start': True
            })

    @api.constrains('shift_type')
    def _check_shift_type(self):
        for rec in self:
            if rec.shift_type == 'one':
                rec.attendance_ids.write({
                    'shift_start': True
                })


class ResourceCalenderAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    shift_start = fields.Boolean(string="Shift Start", )
