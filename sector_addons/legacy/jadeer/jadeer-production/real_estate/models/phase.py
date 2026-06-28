# -*- coding: utf-8 -*
from odoo import models, fields
class Phase(models.Model):
    _inherit = 'project.phase'

    payment_plan_ids = fields.Many2many('payment.plan',string="Payment Plans",ondelete='cascade'  )
