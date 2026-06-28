# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import float_compare


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_status = fields.Selection(selection_add=[('returned',),('closed', 'Closed'), ('bounced', 'Bounced'), ],
                                      ondelete={'code': 'cascade'})
    other_destination_account_id = fields.Many2one('account.account', string='Destination Account')

    # @api.constrains('analytic_account_id')
    # def _check_analytic_account_id_receivable(self):
    #     if self.payment_type == 'inbound':
    #         if self.analytic_account_id:
    #             self.other_destination_account_id = self.analytic_account_id.property_account_receivable_id.id
