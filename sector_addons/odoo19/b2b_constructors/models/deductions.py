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
    amount = fields.Float(string="Amount/Percentage", required=False)
    notes = fields.Text(string="Notes")
    type = fields.Selection( [("amount", "Amount"),
        ("percent", "Percent"),], string="Type",default="amount", required=True)
    account_id = fields.Many2one('account.account',string="Account")

