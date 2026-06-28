# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SocialInsurance(models.Model):
    _name = 'social.insurance'
    _description = 'Social Insurance'

    name = fields.Char(default='Social Insurance')
    employee_max_limit_basic = fields.Monetary(string='Max Limit')
    company_max_limit_basic = fields.Monetary(string='Max Limit')
    employee_min_limit_basic = fields.Monetary(string='Min Limit')
    company_min_limit_basic = fields.Monetary(string='Min Limit')
    employee_basic = fields.Float(string='Basic Insurance Percent', required=True)
    company_basic = fields.Float(string='Basic Insurance Percent', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    employee_max_limit_variable = fields.Monetary(string='Max Limit')
    company_max_limit_variable = fields.Monetary(string='Max Limit')
    employee_min_limit_variable = fields.Monetary(string='Min Limit')
    company_min_limit_variable = fields.Monetary(string='Min Limit')
    employee_variable = fields.Float(string='Variable Insurance Percent')
    company_variable = fields.Float(string='Variable Insurance Percent')
    age_above_60 = fields.Boolean(string="",  )

    @api.constrains("company_id","age_above_60")
    def check_company_insurance(self):
        for rec in self:
            if len(self.search([('company_id','=',rec.company_id.id),('age_above_60','=',True)])) > 1:
                raise ValidationError("Social Insurance Setting For This Company Already Exists1222")
            elif len(self.search([('company_id','=',rec.company_id.id),('age_above_60','=',False)])) > 1:
                raise ValidationError("Social Insurance Setting For This Company Already Exists")
