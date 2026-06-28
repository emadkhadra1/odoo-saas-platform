# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Payslip(models.Model):
    _inherit = 'hr.payslip.line'

    batch_id = fields.Many2one(related="slip_id.payslip_run_id",store=True)