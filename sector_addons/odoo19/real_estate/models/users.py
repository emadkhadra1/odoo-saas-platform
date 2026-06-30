# -*- coding: utf-8 -*-
from datetime import datetime

from werkzeug import urls

from odoo import api, fields, models


class Users(models.Model):
    _inherit = 'res.users'

    def _get_all_products(self):
        return self.env['product.template'].search([])

    products_ids = fields.Many2many('product.template')
