# -*- coding: utf-8 -*-
from __future__ import division
from math import floor,ceil
from odoo import api, fields, models,_

class NewModule(models.Model):
    _name = 'salary.tax.rule'
    _rec_name = 'name'
    _order='level'
    _description = 'New Tax Rule'

    name = fields.Char(string= 'Level',translate=True)
    level = fields.Selection(string="Level",
                             selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),],default='1', required=True, )
    amount_from = fields.Float('From')
    amount_to = fields.Float('To')
    force_amount_from = fields.Float('Force From')
    force_amount_to = fields.Float('Force To')
    tax_rate = fields.Float('Tax Rate (%)')
    tax_exemption = fields.Float('Tax Exemption (%)')
    total_tax = fields.Float('Total Tax',compute='_compute_tax_amount')
    total_discount = fields.Float('Total Discount' ,compute='_compute_discount_amount')
    counter = fields.Integer(string="counter",compute='_compute_tax_counter')

    def _compute_tax_counter(self):
        for rec in self:
            records = self.search([])
            rec.counter = len(records)



    def normal_round(self,n):
        if n - floor(n) < 0.5:
            return floor(n)
        elif n - floor(n) == 0.5:
            return n
        else:
            return ceil(n)

    def _compute_tax_amount(self):
        for rec in self:
            rec.total_tax = 0
            if not rec.level == str(rec.counter):
                total_tax =((rec.amount_to - rec.amount_from) * (rec.tax_rate / 100))
                rec.total_tax = rec.normal_round(total_tax)

    def _compute_discount_amount(self):
        for rec in self:
            total_discount = ((rec.total_tax) * (rec.tax_exemption / 100))
            rec.total_discount = rec.normal_round(total_discount)



    _sql_constraints = [
        ('level_uniq', 'UNIQUE (level)', 'You can not have two rule with the same Level !')
    ]


