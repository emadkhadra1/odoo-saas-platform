# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from dateutil.relativedelta import relativedelta


class Check(models.Model):
    _inherit = 'account.check.deposit'

    def validate_deposit(self):
        res = super(Check, self).validate_deposit()
        for line in self.check_payment_ids:
            line.date = self.deposit_date
        return res

