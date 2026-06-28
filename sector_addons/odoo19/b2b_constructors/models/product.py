# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, pycompat



class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    main_item_id = fields.Many2one("b2b.main.items", string="Main Item", required=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="Sub Item", required=False)

class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    main_item_id = fields.Many2one("b2b.main.items",related='product_id.main_item_id', string="Main Item", required=False)
    sub_item_id = fields.Many2one("b2b.sub.items",related='product_id.sub_item_id',  string="Sub Item", required=False)
