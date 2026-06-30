# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta
class ProductArea(models.Model):
    _name = 'product.area'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('code', required=True, translate=True)
    product_id = fields.Many2one('product.template')
