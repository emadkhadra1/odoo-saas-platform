# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    labor_id = fields.Many2one(comodel_name="construction.labor", string="", required=False, )
    machines_id = fields.Many2one(comodel_name="construction.machine", string="", required=False, )
    tools_id = fields.Many2one(comodel_name="construction.tool", string="", required=False, )