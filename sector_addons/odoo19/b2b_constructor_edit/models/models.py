# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BoqBusinessItemLine(models.Model):
    _name = 'b2b.business.item.line'
    _inherit = 'b2b.business.item.line'

    product_cost = fields.Monetary(string="تكلفة البند", currency_field="currency_id", required=False, )
    supplier_discount = fields.Float(string="خصم المورد (%)",  required=False, )
    sales_tax = fields.Float(string="ضريبة المبيعات (%)",  required=False, )
    customs = fields.Float(string="الجمارك (%)",  required=False, )
    clearance = fields.Float(string="نسبة التخليص (%)",  required=False, )
    product_price = fields.Monetary(string="سعر المنتج", currency_field="currency_id", compute="_compute_product_price", store=True)
    cost_after_discount = fields.Monetary(string="التكلفة بعد الخصم", currency_field="currency_id", compute="_compute_product_price", store=True)
    hockup = fields.Monetary(string="تكلفة الربط", currency_field="currency_id",required=False, )
    labor_install = fields.Monetary(string="تركيب العمالة", currency_field="currency_id",required=False, )
    transportation = fields.Monetary(string="النقل", currency_field="currency_id",required=False, )
    other_cost = fields.Monetary(string="تكلفة أخرى", currency_field="currency_id", required=False, )
    cost = fields.Monetary(string="التكلفة", currency_field="currency_id", compute='_compute_cost', store=True)
    
    @api.depends('product_cost', 'supplier_discount', 'sales_tax', 'clearance', 'customs')
    def _compute_product_price(self):
        for rec in self:
            rec.cost_after_discount = rec.product_cost * (1 - rec.supplier_discount/100)
            rec.product_price = rec.cost_after_discount * (1 + (rec.customs + rec.clearance + rec.sales_tax)/100)

    @api.depends('product_price', 'hockup', 'labor_install', 'transportation', 'other_cost')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.product_price + rec.hockup + rec.labor_install + rec.transportation + rec.other_cost

    @api.onchange('name')
    def _onchange_product_name(self):
        self.uom_id = self.name.uom_id.id
        self.product_cost = self.name.standard_price
        

class B2BIndexation(models.Model):
    _name = 'b2b.indexation'
    _inherit = 'b2b.indexation'

    multiplier = fields.Float(string="المعامل (%)", )
    discount = fields.Float(string="الخصم (%)", default=lambda s: s.purchase_order_id and s.purchase_order_id.discount, )
    social_insurance = fields.Float(string="التأمينات الاجتماعية (%)", )
    contracting = fields.Float(string="نسبة المقاولة (%)", )
    # category = fields.Float(string="التصنيف", digits='Constructor price', compute="_compute_indexation_category", store=True)
    multiplier_category = fields.Float(string="تصنيف المعامل", digits='Constructor price', compute="_compute_indexation_category", store=True)

    @api.onchange('cost', 'multiplier', 'discount', 'social_insurance', 'contracting')
    def _onchange_ratios(self):
        for rec in self:
            rec.category = rec.multiplier_category * (1 + (rec.social_insurance + rec.contracting - rec.discount) / 100)

    @api.onchange('cost', 'multiplier', 'discount', 'social_insurance', 'contracting')
    def _onchnage_calculation_values(self):
        for rec in self:
            rec.category = rec.multiplier_category * (1 + (rec.social_insurance - rec.discount + rec.contracting) / 100)

    @api.depends('cost', 'multiplier', 'discount', 'social_insurance', 'contracting')
    def _compute_indexation_category(self):
        for rec in self:
            rec.multiplier_category = rec.cost * (1 + rec.multiplier/100)


class B2BConstructionBoQ(models.Model):
    _name = 'b2b.construction.boq'
    _inherit = 'b2b.construction.boq'

    multiplier = fields.Float(string="المعامل", )
    discount = fields.Float(string="الخصم (%)", )
    social_insurance = fields.Float(string="التأمينات الاجتماعية (%)", )
    contracting = fields.Float(string="نسبة المقاولة (%)", )
