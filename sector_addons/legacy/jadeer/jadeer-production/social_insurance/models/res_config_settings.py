from odoo import api, fields, models


class Setting(models.TransientModel):
    _inherit = 'res.config.settings'

    insurance_percentage = fields.Float(string="Insurance Percentage",
                                        related="company_id.insurance_percentage", readonly=False,default=75.0)


class Company(models.Model):
    _inherit = 'res.company'

    insurance_percentage = fields.Float(string="Insurance Percentage",defualt=75.0)
