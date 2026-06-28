# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class AttachedArea(models.Model):
    _name = 'attached.area'

    name = fields.Char(string="Name", required=True, )
    unit_type_id = fields.Many2one(comodel_name="unit.type")
