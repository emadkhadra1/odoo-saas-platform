# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Employee(models.Model):
    _inherit = 'hr.employee'

    arabic_name = fields.Char()
    graduation_date = fields.Date()
    salary_structure_id = fields.Char(string="Grade")