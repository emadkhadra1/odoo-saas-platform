# -*- coding: utf-8 -*
from odoo import models, fields
class Phase(models.Model):
    _name = 'project.phase'
    _rec_name = 'name'
    name = fields.Char(string="Name", )
    analytic_tag_id = fields.Many2one('account.analytic.tag',string="Tag", )
    project_id = fields.Many2one('real.estate.project',string="Project", )
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    cost = fields.Float('Cost')
    delivery_date = fields.Date('Delivery Date')