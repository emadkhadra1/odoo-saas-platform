# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class UnitType(models.Model):
    _name = 'unit.type'

    name = fields.Char(string="Name", required=True, )
    project_category_id = fields.Many2one(comodel_name="project.category", string="Category",)
