# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import ValidationError, UserError


class ProductUtility(models.Model):
    _name = 'product.utility'

    name = fields.Many2one('utility.utility',string='Utility', required='true')
    percent = fields.Float('Percent(%)')
    price = fields.Float(string='Price', required=True)
    included_price = fields.Boolean(string='Included In Total Price')
    payment_plan_id = fields.Many2one('payment.plan', string='Payment Plan')
    product_id = fields.Many2one('product.template')
    # @api.onchange('name')
    # def onchange_name(self):
    #     for rec in self:
    #         rec.percent = rec.name.percent

    update_price = fields.Char(compute="onchange_calc_utility_price",store=True)
    update_percent = fields.Char(compute="onchange_calc_utility_percent",store=True)
    @api.onchange('name')
    def onchange_name(self):
        for rec in self:
            for line in self.product_id.project_id.project_utility_ids:
                if rec.name.id == line.utility_id.id:
                    if line.type == 'percent':
                        rec.percent = line.percent
                    elif line.type == 'amount':
                        rec.price = line.percent

    @api.depends('name', 'percent', 'product_id.list_price', 'product_id.price_before_discount')
    def onchange_calc_utility_price(self):
        if not self.env.context.get('stopper1'):
            for rec in self:
                if rec.product_id.price_before_discount:
                    price = rec.product_id.price_before_discount
                else:
                    price = rec.product_id.list_price
                rec.with_context(stopper2=True).price = rec.percent / 100 * price
                rec.update_price = 'Updated'

    @api.depends('price', 'product_id.list_price', 'product_id.price_before_discount')
    def onchange_calc_utility_percent(self):
        if not self.env.context.get('stopper2'):
            for rec in self:
                if rec.product_id.price_before_discount:
                    price = rec.product_id.price_before_discount
                else:
                    price = rec.product_id.list_price
                rec.with_context(stopper1=True).percent = rec.price / price *100
                rec.update_percent = 'Updated'

