# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
# from openerp.osv.orm import setup_modifiers
# from openerp.tools.translate import _
from odoo import models, fields, api
# from openerp.exceptions import Warning
from datetime import date

from datetime import datetime ,date

# from reportlab.graphics.widgetbase import Face
from odoo.exceptions import UserError, ValidationError




class project_unit(models.Model):
    _name = 'project.unit'
    _rec_name = 'name'
    _description = 'project.unit'

    # 
    # def unlink(self):
    # no state here what can i do now
    #     if self.state == 'done':
    #         raise UserError(_('You cannot delete .'))
    #     return super(project_unit, self).unlink()

    def _default_project_id(self):
        res=False
        if self._context.get('active_model') == 'construction.project' and self._context.get('active_ids'):

            project = self.env['construction.project'].browse(self._context.get('active_ids'))
            res=project[0]
        return res

    
    @api.depends('project_item_ids', 'project_item_ids.project_component_ids', 'project_item_ids.project_component_ids.component_cost')
    def _compute_total_unit_cost(self):
        for rec in self:
            rec.total_unit_cost = sum(rec.project_item_ids.mapped('project_component_ids.component_cost'))
        return True

    project_id = fields.Many2one(comodel_name="construction.project",   default=_default_project_id, string="Project",  )
    name = fields.Char("Unit Name", required=True, )


    unit_location = fields.Char(string="Unit Location", required=False, )
    unit_description = fields.Text(string="Unit Description", required=False, )


    project_item_ids = fields.One2many(comodel_name="project.item", inverse_name="unit_id",
                                        string="Project Item Lines", required=False, )

    total_unit_cost = fields.Float(string="Total Unit Cost", compute="_compute_total_unit_cost", store=True, required=False, )
