# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    no_month_days = fields.Integer(string='Number Month Days', related='company_id.no_month_days', readonly=False)

    attendance_period = fields.Boolean(string='Attendance Period', related='company_id.attendance_period',
                                       readonly=False,
                                       implied_group='attendances_structure.attendance_period')


class ResCompany(models.Model):
    _inherit = 'res.company'

    no_month_days = fields.Integer("Number Month Days", default=30)

    attendance_period = fields.Boolean(string='Attendance Period', readonly=False)
