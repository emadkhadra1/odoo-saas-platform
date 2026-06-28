from odoo import fields, models


class AccountAnalyticTag(models.Model):
    _name = "account.analytic.tag"
    _description = "Analytic Tag Compatibility"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer()
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
