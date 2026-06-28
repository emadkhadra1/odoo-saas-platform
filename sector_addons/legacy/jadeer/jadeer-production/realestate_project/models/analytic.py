# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta


class AccountAnalyticAccountInherited(models.Model):
    _inherit = "account.analytic.account"

    # is_unit_project = fields.Boolean(default=False)
    is_project = fields.Boolean(string="Project", )
    # penalty_percentage = fields.Float(string='Penalty Percentage')
    property_account_receivable_id = fields.Many2one('account.account', string='Receivable Account', domain=lambda x: [
        ('user_type_id', '=', x.env.ref('account.data_account_type_receivable').id)], company_dependent=True)
    # credit_account_id = fields.Many2one('account.account', 'Credit Account', company_dependent=True)
    # journal_id = fields.Many2one('account.journal', 'Journal', company_dependent=True)
    # cost_credit_account_id = fields.Many2one('account.account', 'Costing Account', company_dependent=True)
    # cost_debit_account_id = fields.Many2one('account.account', 'Project Under Construction', company_dependent=True)
    # cost_journal_id = fields.Many2one('account.journal', 'Journal', company_dependent=True)
    # property_stock_valuation_account_id = fields.Many2one('account.account', 'Valuation Account', company_dependent=True)


class LeadProject(models.Model):
    _name = 'lead.project'
    _description = 'Lead Project'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('code', required=True, translate=True)
    product_id = fields.Many2one('product.template')
