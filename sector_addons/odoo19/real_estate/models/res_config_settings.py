# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettingsInherited(models.TransientModel):
    _inherit = "res.config.settings"

    booked_days = fields.Integer(string='Max. On Hold Days', related="company_id.booked_days",store=True, default=2,readonly=False)


class Company(models.Model):
    _inherit = "res.company"

    booked_days = fields.Integer(string='Max. On Hold Days', default=2)
