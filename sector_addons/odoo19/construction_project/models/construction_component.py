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
            raise UserError(_('لا يمكن إتمام العملية:\nتحاول حذف مكون معتمد.'))
        return super(project_component, self).unlink()

    @api.depends('item_id', 'product_id')
    def _compute_component_name(self):
        for rec in self:
            name = ''
            if rec.item_id and rec.product_id:
                name = "%s/%s" % (rec.product_id.name, rec.item_id.name)
            rec.name = name
        return True

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id

    def cp_component_confirm(self):
        if self.product_id and self.component_qty and self.component_qty > 0:

            self.write({'state': 'confirm'})

        else:
            raise UserError(_('خطأ! تأكد من إدخال منتج وكمية أكبر من صفر.'))

        return True

    @api.depends('item_id', 'item_id.unit_id')
    def _compute_project_unit(self):
        for rec in self:
            project_id = False
            unit_id = False
            if rec.item_id and rec.item_id.unit_id:
                unit_id = rec.item_id.unit_id.id
                project_id = rec.item_id.unit_id.project_id.id or False
            rec.project_id = project_id
            rec.unit_id = unit_id
        return True

    project_id = fields.Many2one(comodel_name="construction.project", compute="_compute_project_unit", store=True,
                                 string="المشروع", required=False, )
    unit_id = fields.Many2one(comodel_name="project.unit", compute="_compute_project_unit", store=True, string="الوحدة",
                              required=False, )

    name = fields.Char(string="اسم المكون", compute="_compute_component_name", store=True, required=False, )
    item_id = fields.Many2one(comodel_name="project.item", string="البند", required=True, )
    product_id = fields.Many2one(comodel_name="product.product", string="منتج المكون", required=True, )
    product_uom = fields.Many2one('uom.uom', string='وحدة القياس', required=True)
    component_qty = fields.Float(string="الكمية", default=1, required=True, )
    component_cost = fields.Float(string="تكلفة المكون", required=False, )

    component_description = fields.Text(string="وصف المكون", required=False, )
    state = fields.Selection(string="الحالة", default='new', selection=[('new', 'Draft'), ('confirm', 'تأكيد'), ],
                             required=False, )

    # procurement_id = fields.Many2one(comodel_name="procurement.order", copy=False, string="المشتريات",
    #                                  required=False, )

    picking_id = fields.Many2one(comodel_name="stock.picking", copy=False, string="عملية مخزون", required=False, )

    @api.depends('picking_id', 'picking_id.state')
    def _compute_picking_state(self):
        for rec in self:
            rec.picking_state = rec.picking_id.state if rec.picking_id else ''
        return True

    picking_state = fields.Char(string="حالة عملية المخزون", compute="_compute_picking_state", store=True, required=False, )


class product_template(models.Model):
    _inherit = 'product.template'

    constration_product = fields.Boolean(string="???? ???????", )
