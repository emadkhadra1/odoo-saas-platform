# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_notes_pay = fields.Boolean(string='Is Notes Payable', default=False)
    issue_return_account_id = fields.Many2one(comodel_name="account.account", string="Return Account", required=False, )
    issue_bank_account_id = fields.Many2one(comodel_name="account.account", string="Issue Bank Account", domain="[('user_type_id.type','=','liquidity')]")

    utility_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Utility Account Receivable")
