# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Company(models.Model):
    _inherit = 'res.company'

    egyptian_employee_document_ids = fields.Many2many(
        "res.document.type",
        "company_egyptian_document_rel",
        "company_id",
        "egyptian_document_id",
        string="Employee Document Required",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    egyptian_employee_document_ids = fields.Many2many(
        "res.document.type",
        "setting_egyptian_document_rel",
        "setting_id",
        "egyptian_document_id",
        string="Employee Document Required",
        related="company_id.egyptian_employee_document_ids",
        readonly=False
    )