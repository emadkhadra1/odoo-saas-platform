# -*- coding: utf-8 -*-

from odoo import models, fields, api

class company_modifications(models.Model):
    _inherit='res.company'
    type = fields.Selection(string="?????", selection=[('maka', '???'), ('madina', '???????'), ], required=False, )