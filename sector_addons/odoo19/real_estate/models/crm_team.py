# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare


class CRMTeam(models.Model):
    _inherit = 'crm.team'

    product_ids = fields.Many2many('product.template')
