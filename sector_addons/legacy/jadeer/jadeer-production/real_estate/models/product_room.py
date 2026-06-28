# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import ValidationError, UserError

class ProductRooms(models.Model):
    _name = 'product.room'

    name = fields.Char(string='Room', required='true')
    length = fields.Float()
    width = fields.Float()
    area = fields.Float(string='Area', required='true',compute='calc_area')
    notes = fields.Text(string='Notes')
    product_id = fields.Many2one('product.template')
    @api.depends('length','width')
    def calc_area(self):
        for rec in self:
            rec.area = rec.length * rec.width