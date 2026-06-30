# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class AsignItemsWizard(models.TransientModel):
    _name = 'b2b.assign.items.wizard'

    _description = "Construction BOQ Assigned"

    _rec_name = "purchase_order_id"

    def _get_purchase_order_id(self):
        return self._context.get('active_id') if self._context.get('active_id') else None

    entrepreneurs_id = fields.Many2one("b2b.entrepreneurs.wizard", string="المقاولون المسندون", required=False)
    purchase_order_id = fields.Many2one("b2b.construction.boq", string="Construction BOQ", required=False, default=_get_purchase_order_id)
    consructor_id = fields.Many2one("res.partner", string='Contractor', required=False, domain="[('is_constructors', '=', True)]", context="{'default_is_constructors': True}")
    indexation_id = fields.Many2one("b2b.indexation", string='Construction BOQ Item', required=False, domain="[('purchase_order_id', '=', purchase_order_id)]")
    main_item_id = fields.Many2one(related="indexation_id.main_item_id", string="البند الرئيسي", required=True)
    sub_item_id = fields.Many2one(related="indexation_id.sub_item_id", string="البند الفرعي", required=True )
    sub_business_statement_id = fields.Many2one(related="indexation_id.sub_business_statement_id", string="البند الفرعي الثاني", required=True )
    business_statement_id = fields.Many2one(related="indexation_id.business_statement_id", string="Business Statement", required=True)
    business_statement_domain_ids = fields.Many2many(related="purchase_order_id.business_statement_domain_ids")
    uom_id = fields.Many2one(related="business_statement_id.uom_id", string="Unit", readonly=True)
    required_quantity = fields.Float(related="indexation_id.required_quantity", string="Required Quantity", readonly=True)
    # price = fields.Float(related="indexation_id.category", string="Category", readonly=False)
    price = fields.Float(string="Category", readonly=False)
    old_price = fields.Float(string="الفئة السابقة", compute="_calculate_old_assigned", readonly=False)

    percent = fields.Float(string="Assigned Quantity", required=False)
    old_assigned = fields.Float(compute="_calculate_old_assigned", string="المسند سابقا")
    total = fields.Float(compute="_calculate_total", string="Total Cost")

    
    @api.constrains("required_quantity", "percent", "old_assigned")
    def _check_field(self):
        for s in self:
            if s.indexation_id and s.required_quantity < (s.indexation_id.finished_quantity + s.old_assigned):
                raise ValidationError(_("الكمية المسندة أكبر من الكمية المتاحة!"))
            if s.indexation_id and s.indexation_id.category < s.price:
                raise ValidationError(_("السعر المسند أكبر من قيمة البند!"))

    
    @api.depends('indexation_id')
    def _calculate_old_assigned(self):
        entrepreneurs = self.env["b2b.entrepreneurs"]
        for rec in self:
            assigned = 0.0
            price = 0.0
            old = entrepreneurs.search([
                ("purchase_order_id", "=", rec.purchase_order_id.id),
                ("indexation_id", "=", rec.indexation_id.id),
            ])

            for line in old:
                assigned += line.percent
                price += line.price
            rec.old_assigned = assigned
            rec.old_price = price

    
    @api.depends('price', 'percent')
    def _calculate_total(self):
        for rec in self:
            rec.total = rec.price * rec.percent


    @api.onchange('sub_item_id')
    def onchange_sub_item_id(self):
        for rec in self:
            if rec.sub_item_id:
                rec.main_item_id = rec.sub_item_id.main_item_id.id

    @api.onchange('business_statement_id')
    def onchange_business_statement_id(self):
        for rec in self:
            if rec.business_statement_id:
                rec.sub_business_statement_id = rec.business_statement_id.sub_business_statement_id
                rec.sub_item_id = rec.business_statement_id.sub_item_id
                rec.main_item_id = rec.business_statement_id.sub_item_id.main_item_id
