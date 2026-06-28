# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _rec_name = 'category'
    _inherit = ['mail.thread']
    category = fields.Char('Name', required='1', track_visibility='onchange', )
    code = fields.Char('Code', required='1', track_visibility='onchange')
