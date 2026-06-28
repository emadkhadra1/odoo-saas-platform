# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class Floor(models.Model):
    _name = 'building.floor'
    _rec_name = 'name'

    building_id = fields.Many2one('project.building','Building')
    name = fields.Char(string="Name", )
    analytic_tag_id = fields.Many2one('account.analytic.tag',string="Tag", )
    project_id = fields.Many2one('real.estate.project',string="Project", )
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    code = fields.Char('Code')
    cost = fields.Float('Cost')
    description = fields.Text()
    _sql_constraints = [
        ("number_unique", "unique(name,building_id, project_id)", "Number of floor Unique per building")
    ]
    # @api.onchange('name')
    # def onchange_name(self):
    #     if self.name >9 :
    #         self.code = self.name
    #     else:
    #         self.code = '0' + str(self.name)


