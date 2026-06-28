# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    other_destination_account_id = fields.Many2one('account.account', string ='Destination Account')

    # @api.constrains('analytic_account_id')
    # def _check_analytic_account_id_receivable(self):
    #     if self.payment_type == 'inbound':
    #         if self.analytic_account_id :
    #             self.other_destination_account_id = self.analytic_account_id.property_account_receivable_id.id
