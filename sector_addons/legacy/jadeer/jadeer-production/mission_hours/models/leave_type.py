# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Leave(models.Model):
    _inherit = 'hr.leave.type'

    mission_hours = fields.Boolean(string="Is Permission Hours", )
    occurrence_number = fields.Float(string="Occurrence Number", required=False, )
    min_hour_per_time = fields.Float(string="Minimum Hours Per Time", required=False, )
    max_hour_per_time = fields.Float(string="Maximum Hours Per Time")

    @api.constrains('request_unit', 'mission_hours', )
    def _check_mission_hours(self):
        for line in self:
            if line.mission_hours and line.request_unit != 'hour':
                raise exceptions.ValidationError('Time Off must in Hours when Mission Hours checked !')
