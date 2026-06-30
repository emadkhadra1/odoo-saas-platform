# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class Entrepreneurs(models.Model):
    _name = 'b2b.entrepreneurs'
    _inherit = ['mail.thread']
    _description = "إسناد جدول الكميات"

    _rec_name = "indexation_id"

    purchase_order_id = fields.Many2one("b2b.construction.boq", string="جدول كميات المقاولات", required=True, tracking=True, ondelete='cascade',)
    project_id = fields.Many2one(related="purchase_order_id.project_id", string="المشروع", readonly=True, store=True, tracking=True)
    consructor_id = fields.Many2one("res.partner", string='المقاول', required=False, domain="[('is_constructors', '=', True)]", context="{'default_is_constructors': True}", tracking=True)
    indexation_id = fields.Many2one("b2b.indexation", string='بند جدول الكميات', required=False, domain="[('purchase_order_id', '=', purchase_order_id)]")
    main_item_id = fields.Many2one(related="indexation_id.main_item_id", string="????? ???????", required=True)
    sub_item_id = fields.Many2one(related="indexation_id.sub_item_id", string="????? ??????", required=False )
    business_statement_id = fields.Many2one(related="indexation_id.business_statement_id",  string="بيان الأعمال", required=False)
    sub_business_statement_id = fields.Many2one(related="indexation_id.sub_business_statement_id",  string="????? ?????? ??????", required=False)
    uom_id = fields.Many2one(related="business_statement_id.uom_id", string="الوحدة", readonly=True, store=True)
    required_quantity = fields.Float(related="indexation_id.required_quantity", string="الكمية المطلوبة", tracking=True)
    # price = fields.Float(related="indexation_id.category", string="التصنيف", readonly=True,digits='Constructor price')
    price = fields.Float( string="التصنيف", readonly=False,digits='Constructor price')
    type_ids = fields.Many2many(related="business_statement_id.type_ids")
    type_id = fields.Many2one(comodel_name="b2b.business.items.type", string="النوع", required=False,
                              domain="[('id', 'in', type_ids)]")
    labor_install = fields.Float(string="تركيب العمالة", compute="compute_labour_install")
    percent = fields.Float(string="الكمية المسندة", required=True)
    old_assigned = fields.Float(compute="_calculate_old_assigned", string="?????? ?????")
    total = fields.Float(compute="_calculate_total", string="إجمالي التكلفة")

    @api.depends('business_statement_id')
    def compute_labour_install(self):
        for rec in self:
            rec.labor_install = sum(lab.labor_install for lab in rec.business_statement_id.line_ids)

    
    @api.depends('indexation_id')
    def _calculate_old_assigned(self):
        for rec in self:
            assigned = 0.0
            old = self.search([
                ("purchase_order_id", "=", rec.purchase_order_id.id),
                ("indexation_id", "=", rec.indexation_id.id),
            ])

            for line in old:
                assigned += line.percent

            rec.old_assigned = assigned

    
    @api.depends('price', 'percent')
    def _calculate_total(self):
        for rec in self:
            rec.total = rec.price * rec.percent
