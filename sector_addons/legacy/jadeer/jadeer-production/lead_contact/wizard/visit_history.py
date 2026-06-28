# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
class VisitNotesHistory(models.Model):
    _name = "visit.history"

    visit_notes = fields.Text("Visit Notes")
    visit_date = fields.Datetime(string="Visit Date", required=False,)
    lead_id = fields.Many2one('crm.lead')