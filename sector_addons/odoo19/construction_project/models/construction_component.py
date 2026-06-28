# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
# from openerp.osv.orm import setup_modifiers
# from openerp.tools.translate import _
from odoo import models, fields, api
from datetime import date

from datetime import datetime, date

# from reportlab.graphics.widgetbase import Face
from odoo.exceptions import UserError, ValidationError


class project_component(models.Model):
    _name = 'project.component'
    _rec_name = 'name'
    _description = 'project.component'
    _order = 'state DESC'

    def unlink(self):

        if self.state == 'confirm':
            raise UserError(_(
                'The operation cannot be completed:\nYou are trying to delete Component Confirmed.'))
        return super(project_component, self).unlink()

    @api.depends('item_id', 'product_id')
    def _compute_component_name(self):
        name = ''
        if self.item_id and self.product_id:
            name = self.product_id.name + "/" + self.item_id.name

        self.name = name

        return True

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id

    def cp_component_confirm(self):
        if self.product_id and self.component_qty and self.component_qty > 0:

            self.write({'state': 'confirm'})

        else:
            raise UserError(_('Error !Cannot Confirm The Item : Make Sure The Line Have Peoduct And QTY > 0 '))

        return True

    @api.depends('item_id', 'item_id.unit_id')
    def _compute_project_unit(self):
        project_id = False
        unit_id = False
        if self.item_id and self.item_id.unit_id and self.item_id.unit_id.project_id:
            if self.item_id.unit_id.project_id:
                project_id = self.item_id.unit_id.project_id.id
                unit_id = self.item_id.unit_id.id
        self.project_id = project_id
        self.unit_id = unit_id

        return True

    project_id = fields.Many2one(comodel_name="construction.project", compute="_compute_project_unit", store=True,
                                 string="Project", required=False, )
    unit_id = fields.Many2one(comodel_name="project.unit", compute="_compute_project_unit", store=True, string="Unit",
                              required=False, )

    name = fields.Char(string="Component Name", compute="_compute_component_name", store=True, required=False, )
    item_id = fields.Many2one(comodel_name="project.item", string="Item", required=True, )
    product_id = fields.Many2one(comodel_name="product.product", string="Component Product", required=True, )
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    component_qty = fields.Float(string="QTY", default=1, required=True, )
    component_cost = fields.Float(string="Component Cost", required=False, )

    component_description = fields.Text(string="Component Description", required=False, )
    state = fields.Selection(string="State", default='new', selection=[('new', 'Draft'), ('confirm', 'Confirm'), ],
                             required=False, )

    # procurement_id = fields.Many2one(comodel_name="procurement.order", copy=False, string="Procurement",
    #                                  required=False, )

    picking_id = fields.Many2one(comodel_name="stock.picking", copy=False, string="Picking", required=False, )

    @api.depends('picking_id', 'picking_id.state')
    def _compute_picking_state(self):
        picking_state = ''
        if self.picking_id:
            picking_state = self.picking_id.state

        self.picking_state = picking_state
        return True

    picking_state = fields.Char(string="Picking State", compute="_compute_picking_state", store=True, required=False, )


class product_template(models.Model):
    _inherit = 'product.template'

    constration_product = fields.Boolean(string="Constration Product", )
