# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SalaryTax(models.Model):
    _inherit = 'hr.salary.rule'

    taxable = fields.Boolean(string="Under Tax", )



