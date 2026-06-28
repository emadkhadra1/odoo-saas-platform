# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    write_off = fields.Boolean(string='Write Off', default=False)
    is_check = fields.Boolean(string='Cheque', default=False)
    is_return_check = fields.Boolean(string='Return Cheque', default=False)
    credit_check_account_id = fields.Many2one('account.account', string='Cheque Credit Account')
    debit_check_account_id = fields.Many2one('account.account', string='Cheque Debit Account')
    return_credit_check_account_id = fields.Many2one('account.account', string='Return Cheque Credit Account')
    return_debit_check_account_id = fields.Many2one('account.account', string='Return Cheque Debit Account')
    bad_debit_account_id = fields.Many2one('account.account', string='Bad Debit Account')
    is_notes_rec = fields.Boolean(string='Is Notes Receivable', default=False)
    type_of_check = fields.Selection([('reservation','Reservation'),('utility', 'Utility'),('installment', 'Installment')],
                                     string='Type of Check')

    @api.onchange('is_notes_rec')
    def onchange_is_notes_rec(self):
        for line in self:
            if line.is_notes_rec == False:
                line.credit_check_account_id = False
                line.debit_check_account_id = False
                line.return_credit_check_account_id = False
                line.return_debit_check_account_id = False

    @api.onchange('return_credit_check_account_id')
    def onchange_return_credit_check_account_id(self):
        for account in self:
            if account.return_credit_check_account_id:
                account.return_debit_check_account_id = account.return_credit_check_account_id

    @api.onchange('credit_check_account_id')
    def onchange_credit_check_account_id(self):
        for account in self:
            if account.credit_check_account_id:
                account.debit_check_account_id = account.credit_check_account_id
