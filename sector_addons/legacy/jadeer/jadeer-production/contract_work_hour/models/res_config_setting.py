from odoo import models, fields, api, _, exceptions


class Company(models.Model):
    _inherit = 'res.company'

    use_work_hour = fields.Boolean()


class ConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    use_work_hour = fields.Boolean(related="company_id.use_work_hour", readonly=False)
