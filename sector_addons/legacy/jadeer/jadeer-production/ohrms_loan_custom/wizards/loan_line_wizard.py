# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class LoanLineWizard(models.TransientModel):
    _inherit = 'loan.line.wizard'

    def update_amount(self):
        super(LoanLineWizard, self).update_amount()
        if self.old_amount != self.amount:
            self.loan_id.is_rescheduled = True
