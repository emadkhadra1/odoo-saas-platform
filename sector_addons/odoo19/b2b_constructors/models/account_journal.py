# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_construction_journal = fields.Boolean(string='????? ?????????')
