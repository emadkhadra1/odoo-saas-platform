from odoo import models, fields, api, _, exceptions


class Company(models.Model):
    _inherit = 'res.company'

    loan_hr_manager_id = fields.Many2one('res.users','Hr Manager')
    loan_cfo_manager_id = fields.Many2one('res.users','CFO')
    loan_ceo_manager_id = fields.Many2one('res.users','CEO')


class ConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    loan_hr_manager_id = fields.Many2one('res.users','Hr Manager',related="company_id.loan_hr_manager_id", readonly=False)
    loan_cfo_manager_id = fields.Many2one('res.users','CFO',related="company_id.loan_cfo_manager_id", readonly=False)
    loan_ceo_manager_id = fields.Many2one('res.users','CEO',related="company_id.loan_ceo_manager_id", readonly=False)