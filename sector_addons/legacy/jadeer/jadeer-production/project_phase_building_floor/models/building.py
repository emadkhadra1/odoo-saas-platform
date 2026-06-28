# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class Building(models.Model):
    _name = 'project.building'
    _rec_name = 'code'

    analytic_tag_id = fields.Many2one('account.analytic.tag', string="Tag",)
    phase_id = fields.Many2one('project.phase', string="Phase", )
    project_id = fields.Many2one('real.estate.project', string="Project", )
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    code = fields.Char('Code')
    cost = fields.Float('Cost')
    description = fields.Text()
    @api.onchange('project_id')
    def onchange_project(self):
        self.phase_id = False

    _sql_constraints = [
        ("code_unique", "unique(code, project_id)", "Code of building Unique per project")
    ]