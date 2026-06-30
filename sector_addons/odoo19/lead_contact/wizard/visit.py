# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare


class VisitNotes(models.TransientModel):
    _name = "visit.notes"
    _description = 'Visit Notes'

    name = fields.Text('Notes', required=True, )
    visit_date = fields.Datetime(string="Visit Date", required=False, )

    def apply(self):
        lead = self.env.context.get('lead_id')
        if lead:
            lead = self.env['crm.lead'].browse(lead)
            lead.visit_notes = self.name
            lead.visit_date = self.visit_date
            lead.actual_visit = True
            self.env['visit.history'].create({'lead_id': lead.id,
                                              'visit_notes': self.name,
                                              'visit_date': self.visit_date,
                                              })