# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class Constructors(models.Model):
    _inherit = "res.partner"

    is_constructors = fields.Boolean(string="Is a Constructors")
    deduction_ids = fields.One2many('res.partner.deduction','partner_id',string="Deductions lines")


class Project(models.Model):
    _inherit = 'construction.project'

    project_constructor_ids = fields.One2many('project.constructor', 'project_id')
    owner_downpayment = fields.Float(string="Owner DownPayment")


class ProjectConstructor(models.Model):
    _name = 'project.constructor'

    constructor_id = fields.Many2one("res.partner", string='Contractor', required=False,
                                     domain="[('is_constructors', '=', True)]",
                                     context="{'default_is_constructors': True}")
    downpayment = fields.Float(string="Downpayment Percentage")
    project_id = fields.Many2one(comodel_name="construction.project", string="", required=False)


class Constructorsdecuation(models.Model):
    _name = "res.partner.deduction"

    partner_id = fields.Many2one('res.partner',string="Constructor")
    deduction_id = fields.Many2one('b2b.deductions',string="Deductions")
    name = fields.Char(related='deduction_id.name',sring="Deduction Name", required=True)
    amount = fields.Float(related='deduction_id.amount',string="Amount/Percentage", required=False)
    type = fields.Selection( [("amount", "Amount"),
        ("percent", "Percent"),],related='deduction_id.type', string="Type",default="amount", required=True)
    account_id = fields.Many2one('account.account',related='deduction_id.account_id',string="Account")
