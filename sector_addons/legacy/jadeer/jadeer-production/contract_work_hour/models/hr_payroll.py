# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class HrPayroll(models.Model):
    _inherit = 'hr.payslip'

    def get_hour_value(self):
        hour_value = super(HrPayroll, self).get_hour_value()
        if self.company_id.use_work_hour:
            hour_value = self.contract_id.hour_value
        return hour_value
