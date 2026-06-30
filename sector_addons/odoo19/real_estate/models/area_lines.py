# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import ValidationError, UserError

class ProductRooms(models.Model):
    _name = 'attached.area.line'
    _rec_name = 'attached_area_id'

    attached_area_id = fields.Many2one('attached.area',string='Attached Area', )
    total = fields.Float(string='Total',compute='calc_total',store=True )
    area = fields.Float(string='Area', )
    price = fields.Float(string='Price')
    product_id = fields.Many2one('product.template')

    # fixed_discount = fields.Float(string="Fixed Disc.", default=0.000)
    #
    # discount = fields.Float(string='% Disc.', digits='Discount', default=0.000)

    # @api.onchange("discount")
    # def _onchange_discount(self):
    #     for line in self:
    #         if line.discount != 0:
    #             self.fixed_discount = 0.0
    #             fixed_discount = (line.price * line.area) * (line.discount / 100.0)
    #             line.update({"fixed_discount": fixed_discount})
    #         if line.discount == 0:
    #             fixed_discount = 0.000
    #             line.update({"fixed_discount": fixed_discount})
    #
    # @api.onchange("fixed_discount")
    # def _onchange_fixed_discount(self):
    #     for line in self:
    #         if line.fixed_discount != 0:
    #             self.discount = 0.0
    #             discount = ((self.area * self.price) - ((self.area * self.price) - self.fixed_discount)) / (self.area * self.price) * 100 or 0.0
    #             line.update({"discount": discount})
    #         if line.fixed_discount == 0:
    #             discount = 0.0
    #             line.update({"discount": discount})
    @api.depends('price','area')
    def calc_total(self):
        for rec in self:
            rec.total = (rec.price * rec.area)