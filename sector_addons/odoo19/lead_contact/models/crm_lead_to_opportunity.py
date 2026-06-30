# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

class Lead2Opportunity(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner'

    has_contact = fields.Boolean()
    has_opp = fields.Boolean()

    # @api.onchange('name','has_opp')
    # def onchange_name_opp(self):
    #     if self.name=='merge' and self.has_opp and self.env.context.get('has_opp'):
    #         self.opportunity_ids = self.env.context.get('has_opp') + self.env.context.get('active_ids',[])
    #     else:
    #         self.opportunity_ids = False

    @api.model
    def _find_matching_partner(self):
        res = super(Lead2Opportunity, self)._find_matching_partner()
        if self._context.get('default_partner_id'):
            return self._context.get('default_partner_id')
        return res