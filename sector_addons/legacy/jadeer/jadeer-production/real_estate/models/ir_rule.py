# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class IrRule(models.Model):
    _inherit = 'ir.rule'

    # @api.model
    # def _eval_context(self):
    #     res = super(IrRule, self)._eval_context()
    #     sale_team = self.env['crm.team']
    #     if self.env.user:
    #         sale_team = sale_team.sudo().search([('member_ids', 'in', self.env.user.id)], limit=1)
    #     res.update({
    #         'sale_team': sale_team,
    #     })
    #     return res
