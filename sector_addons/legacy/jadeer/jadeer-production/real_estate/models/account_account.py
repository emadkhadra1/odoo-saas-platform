# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class AccountInherit(models.Model):
    _inherit = 'account.account'

    is_costing = fields.Boolean('Costing')

