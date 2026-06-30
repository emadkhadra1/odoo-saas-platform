# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime


class Utility(models.Model):
    _name = "utility.utility"
    name = fields.Char('Name')
    code = fields.Char('Code')
    account_id = fields.Many2one('account.account','Account')
    percent = fields.Float('Percent(%)')
    receivable_account_id = fields.Many2one('account.account', string='Receivable Account',
                                            domain=[('user_type_id.type', '=', 'receivable')],
                                            default=lambda
                                                self: self.env.company.account_default_pos_receivable_account_id)

    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.company,
                                 )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", domain=[('type', '=', 'sale')], )

    # @api.constrains('percent')
    # def _check_total_qty(self):
    #     for line in self:
    #         if line.percent < 0 or line.percent > 100:
    #             raise exceptions.ValidationError('Percent must be >= 0 or <= 100 !')


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'name': _("%s (copy)" % self.name), 'field_ids': []})
        return super(Utility, self).copy(default)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique!'),
    ]