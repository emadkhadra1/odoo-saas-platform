# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.exceptions import ValidationError, UserError


class Setting(models.TransientModel):
    _inherit = 'res.config.settings'

    expiry_duration = fields.Integer(string="Expiry Duration",related="company_id.expiry_duration", readonly=False)


class Company(models.Model):
    _inherit = 'res.company'

    expiry_duration = fields.Integer(string="Expiry Duration")
