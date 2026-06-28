# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    attendance_id = fields.Many2one('attendance.structure', string='Attendance Structure')
