# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval

import json
from lxml import etree


class Lead2Opportunity(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    reason = fields.Char(string="Reason", required=False, )

    def action_apply(self):
        self.lead_id.convert_opp_reason = self.reason
        self.lead_id.converted_to_opp = True
        if self.action == 'exist':
            self.lead_id.from_existing_partner = True
            self.lead_id.mobile = self.partner_id.mobile
            self.lead_id.partner_national_id = self.partner_id.partner_national_id
            self.lead_id.partner_international_id = self.partner_id.partner_international_id
        return super(Lead2Opportunity, self).action_apply()
