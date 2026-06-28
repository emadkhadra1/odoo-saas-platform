# -*- coding: utf-8 -*-
from odoo import api, fields, models
import time
from datetime import datetime, timedelta
from dateutil import relativedelta








class construction_receive_order_line(models.Model):
    _inherit = 'construction.receive.order.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        unit_cost = 0
        self.unit_price = self.product_id.list_price
        self.product_category_id = self.product_id.categ_id


    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        res = {}
        if self.product_category_id:
            res['domain'] = {'product_id': [('categ_id', '=', self.product_category_id.id)]}
        else:
            res['domain'] = {'product_id': []}
        return res
