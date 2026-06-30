# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False,
                                          help="Link this project to an analytic account if you need financial management on projects. "
                                               "It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")

    @api.onchange('destination_account_id')
    def onchange_destination_account_id(self):
        if self.destination_account_id:
            res = self.env['account.analytic.default'].sudo().search(
                [('account_id', '=', self.destination_account_id.id)], limit=1)
            if res:
                self.analytic_account_id = res.analytic_id.id
                self.analytic_tag_ids = res.analytic_tag_ids.ids

    def _prepare_payment_moves(self):
        all_vals = []
        for payment in self:
            vals = super(AccountPayment, payment)._prepare_payment_moves()
            for line in vals:
                for l in line.get('line_ids'):
                    l[2].update({
                        'analytic_account_id': payment.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, payment.analytic_tag_ids.ids)],
                    })
            all_vals += vals
        return all_vals
