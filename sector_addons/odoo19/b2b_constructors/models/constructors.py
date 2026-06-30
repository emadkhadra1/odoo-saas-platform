# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class Constructors(models.Model):
    _inherit = "res.partner"

    is_constructors = fields.Boolean(string="مقاول")
    deduction_ids = fields.One2many('res.partner.deduction','partner_id',string="بنود الخصومات")


class Project(models.Model):
    _inherit = 'construction.project'

    project_constructor_ids = fields.One2many('project.constructor', 'project_id')
    owner_downpayment = fields.Float(string="دفعة مقدمة من المالك")


class ProjectConstructor(models.Model):
    _name = 'project.constructor'

    constructor_id = fields.Many2one("res.partner", string='المقاول', required=False,
                                     domain="[('is_constructors', '=', True)]",
                                     context="{'default_is_constructors': True}")
    downpayment = fields.Float(string="نسبة الدفعة المقدمة")
    project_id = fields.Many2one(comodel_name="construction.project", string="", required=False)


class Constructorsdecuation(models.Model):
    _name = "res.partner.deduction"

    partner_id = fields.Many2one('res.partner',string="المقاول")
    deduction_id = fields.Many2one('b2b.deductions',string="الخصومات")
    name = fields.Char(related='deduction_id.name',sring="Deduction Name", required=True)
    amount = fields.Float(related='deduction_id.amount',string="مبلغ/نسبة", required=False)
    type = fields.Selection( [("amount", "المبلغ"),
        ("percent", "النسبة"),],related='deduction_id.type', string="النوع",default="amount", required=True)
    account_id = fields.Many2one('account.account',related='deduction_id.account_id',string="الحساب")
