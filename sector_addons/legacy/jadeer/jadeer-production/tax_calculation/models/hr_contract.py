# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    apply_tax = fields.Boolean(string="Apply Tax",default=True)

