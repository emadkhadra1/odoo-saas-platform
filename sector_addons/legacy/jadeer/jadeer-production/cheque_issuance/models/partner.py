# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Partner(models.Model):
    _inherit = 'res.partner'

    is_advance_payment_client = fields.Boolean(string="Is Advance Payment Vendor ?", )

    advance_payment_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Advance Payment Account",
        required=False
    )
