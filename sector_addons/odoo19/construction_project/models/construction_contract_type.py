# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions

class NewModule(models.Model):
    _name = 'contract.type'
    _rec_name = 'contract_type'

    contract_type = fields.Char(string="Contract Type", required=False, )

    value = fields.Float(string="Value",  required=False, )

