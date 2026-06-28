# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Payment(models.Model):
    _inherit = 'account.payment'

    payment_type_check = fields.Selection([
        ('payment', "Payment"),
        ('check', "Cheque"),
    ], default='payment', required=True, string='Payment Method')
    payment_status = fields.Selection([
        ('posted', 'Posted'),
        ('deposit', 'Deposit'),
        ('collected', 'Collected'),
        ('returned', 'Returned'),
        ('returned_to_customer', 'Returned To Customer'),
        ('recycle', 'Recycle'),
        ('re-check', 'Re-Check'),
        ('cash', 'Cash'),
        ('writeoff', 'Write-Off')
    ], copy=False, string="Status", readonly=True, tracking=True, )

    def action_post(self):
        super(Payment, self).action_post()
        for payment in self:
            if payment.state == 'posted':
                payment.payment_status = 'posted'
