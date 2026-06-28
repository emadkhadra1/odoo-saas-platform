# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from dateutil.relativedelta import relativedelta


class Check(models.Model):
    _inherit = 'account.payment'
    collected_date = fields.Date(string="Collected Date",readonly=True)

    def action_open_collect_wizard(self):
        for rec in self:
            arr = []
            fee_amount = 0
            fee_percent = 0
            analytic_account_id = rec.analytic_account_id
            if rec.due_date < date.today():
                apply_penalty = rec.check_apply_penalty(date.today(),rec.due_date, analytic_account_id.fee_percent_type)
                if apply_penalty:
                    difference = date.today() - Date.from_string(rec.due_date)
                    if analytic_account_id:
                        fee_percent = analytic_account_id.fee_percent
                        fee_percent_type = analytic_account_id.fee_percent_type
                        if fee_percent:
                            if fee_percent_type == 'daily':
                                days = difference.days
                                fee_amount = ((fee_percent / 100) / 365) * days * rec.amount
                            elif fee_percent_type == 'monthly':
                                difference = relativedelta(date.today(), Date.from_string(rec.due_date))
                                months = difference.months
                                fee_amount = ((fee_percent / 100) / 12) * months * rec.amount

                        arr.append((0, 0, {
                            'payment_id': rec.id,
                            'analytic_account_id': analytic_account_id.id,
                            'fee_percent': fee_percent,
                            'fee_amount': fee_amount,
                            'apply_fee':True,
                        }))
                    else:
                        arr.append((0, 0, {
                            'payment_id': rec.id,
                            'is_no_fee': True
                        }))
            else:
                arr.append((0, 0, {
                    'payment_id': rec.id,
                    'is_no_fee': True
                }))
            return {
                'name': _("Collect Wizard"),
                'view_type': 'form',
                'context': {
                    'default_account_payment_id': self.id,
                    'default_line_ids': arr,
                },
                'view_mode': 'form',
                'res_model': 'collect.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    # def check_apply_penalty(self, date_due, penalty_type):
    #     if penalty_type == 'daily':
    #         date_due = date_due + timedelta(days=1)
    #         if date_due < date.today():
    #             return True
    #         else:
    #             return False
    #     else:
    #         date_due = date_due + relativedelta(months=1)
    #         if date_due < date.today():
    #             return True
    #         else:
    #             return False
