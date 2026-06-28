# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta


class payment_plan(models.Model):
    _name = 'payment.plan'

    name = fields.Char('Name', required='true')

    # sales_person = fields.Many2many('res.users', string='Sales Person')
    discount_type = fields.Selection([('amount', 'Amount'), ('percentage', 'Percentage')], default='amount', string='Discount')
    discount_amount = fields.Float('Amount')
    discount_percentage = fields.Float('Percentage')

    payment_line_ids = fields.One2many('payment.plan.line', 'payment_id')
    interset = fields.Float('Interest',digits=(3, 20), default=0.0)


    @api.constrains('payment_line_ids')
    def calulate_percentage(self):
        for record in self:
            sum = 0
            if len(record.payment_line_ids) > 0:
                for line in record.payment_line_ids:
                    if line.percentage > 0:
                        sum += line.percentage
                    else:
                        raise ValidationError("The Percentage can't be 0 %")
                    if line.non_return < 0:
                        raise ValidationError("The Non Returned Amount must be positive")
                    if line.value < 0:
                        raise ValidationError("The Value must be greater than Or Equale 0")
                if round(sum,0) != 100:
                    raise ValidationError('The total Percentage must be equal to 100 %')


class payment_plan_line(models.Model):
    _name = 'payment.plan.line'

    pricing_unit = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], default='percentage', string='Pricing Unit')
    value = fields.Integer('Value', required='true',default=1)
    percentage = fields.Float('Percentage (%)', required=True)
    pay_type = fields.Selection(
        [('contracting', 'DownPayment'), ('delivery', 'Delivery'),('maintenance','Maintenance'),
         ('installment', 'Installment'),('reservation','Reservation')], default='contracting', string='Type')
    duration = fields.Selection(selection=[('monthly', 'شهرى'),('quarterly', 'ربع سنوي'),
                                           ('mid', 'نص سنوي'),('annual','سنوي') ], required=False, )
    schedule_period = fields.Selection([('day', 'Day'), ('month', 'Month')], string='Unit')
    non_return = fields.Integer('Non-Returned Amount', required=True, default=0)
    amount = fields.Integer('Amount')
    unit_amount = fields.Float('Installment Amount', compute='_compute_price_per_unit', readonly=True)
    is_product = fields.Boolean(default=False)
    no_of_installements = fields.Integer('# Installments', default=1, required=True)
    payment_id = fields.Many2one('payment.plan', 'Payment Reference')
    product_id = fields.Many2one('product.template')
    offer_id = fields.Many2one('offer.payment.plan')
    start_date = fields.Datetime(string="Start Date", readonly=True)
    line_interset = fields.Float('Interset', digits=(3, 8), default=0.0)

    @api.onchange('duration')
    def onchange_duration(self):
        if self.duration == 'monthly':
            self.value = 1
            self.schedule_period = 'month'
        elif self.duration == 'quarterly':
            self.value = 3
            self.schedule_period = 'month'
        elif self.duration == 'mid':
            self.value = 6
            self.schedule_period = 'month'
        elif self.duration == 'annual':
            self.value = 12
            self.schedule_period = 'month'

    @api.depends('no_of_installements', 'amount')
    def _compute_price_per_unit(self):
        for record in self:
            record.unit_amount = record.amount / record.no_of_installements


class product_real_estate(models.Model):
    _name = 'offer.payment.plan'

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    product_tmpl_id = fields.Many2one('product.template', string='Unit',
                                      domain="[('state', '=', 'sale'), ('is_residential', '=',True)]", )

    payment_plan_id = fields.Many2one('payment.plan', string='Payment Plan')
    payment_plan_ids = fields.One2many('payment.plan.line', 'offer_id')
    start_date = fields.Datetime(string='Start Date')

    partner_id = fields.Many2one('res.partner', string='Customer', track_visibility='onchange',)
    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team,
                              oldname='section_id')

    campaign_id = fields.Many2one('utm.campaign', string='Campaign')
    source_id = fields.Many2one('utm.source', string='Source')
    medium_id = fields.Many2one('utm.medium', string='Medium')
    crm_id = fields.Many2one('crm.lead')


    @api.onchange('product_tmpl_id')
    def _get_payment_plan_id(self):
        planlist = []
        if self.product_tmpl_id:
            for plan in self.product_tmpl_id.payment_plan_id:
                planlist.append(plan.id)
            return {'domain': {'payment_plan_id': [('id', 'in', planlist)]}}


    def calculate_payment_plan(self):
        plan_list = []
        count = 0
        result = 0.0
        x = 0
        date_time = 0
        date_time_str = 0
        for plan in self.payment_plan_id:
            for line in plan.payment_line_ids:

                if count == 0:
                    line.start_date = self.start_date
                    result = line.no_of_installements * line.value
                    line_date = line.schedule_period
                    x = line.start_date
                else:
                    if line_date == 'month':
                        line.start_date = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') + relativedelta(
                            months=+result)
                        x = line.start_date
                    if line_date == 'day':
                        line.start_date = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') + timedelta(days=+result)
                        x = line.start_date
                result = line.no_of_installements * line.value
                line_date = line.schedule_period
                count += 1
                plan_list.append(line.id)
        self.payment_plan_ids = [(6, 0, plan_list)]
        return {
            "type": "ir.actions.do_nothing",
        }
