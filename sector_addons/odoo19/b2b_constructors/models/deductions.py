# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class Deductions(models.Model):
    _name = 'b2b.deductions'

    name = fields.Char(sring="Deduction Name", required=True)
    amount = fields.Float(string="مبلغ/نسبة", required=False)
    notes = fields.Text(string="ملاحظات")
    type = fields.Selection( [("amount", "المبلغ"),
        ("percent", "النسبة"),], string="النوع",default="amount", required=True)
    account_id = fields.Many2one('account.account',string="الحساب")

