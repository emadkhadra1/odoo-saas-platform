# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    second_sub_item_id = fields.Many2one(comodel_name="b2b.sub.business.items", string="بند أعمال فرعي ثاني", required=False, )

    def click_constration_product(self):
        if self.constration_product:
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.id)], limit=1)
            line_ids =[]
            bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_id.product_tmpl_id.id), ('bom_type', '=', 'costing')], limit=1)
            for bom_line in bom_id.bom_line_ids:
                line_ids.append((0, 0, {'name': bom_line.product_id.id, 'uom_id': bom_line.product_uom_id.id, 'qty': bom_line.product_qty,
                                        'product_cost': bom_line.product_cost, 'supplier_discount': bom_line.supplier_discount,
                                        'sales_tax': bom_line.sales_tax, 'customs': bom_line.customs, 'clearance': bom_line.clearance,
                                        'product_price': bom_line.product_price, 'cost_after_discount': bom_line.cost_after_discount,
                                        'hockup': bom_line.hockup, 'labor_install': bom_line.labor_install,
                                        'transportation': bom_line.transportation, 'other_cost': bom_line.other_cost,
                                        'cost': bom_line.cost}))
            values = {'name': self.name, 'code': self.default_code, 'main_item_id': self.main_item_id.id, 'sub_item_id': self.sub_item_id.id, 'uom_id': product_id.uom_id.id,
                      'sub_business_statement_id': self.second_sub_item_id.id, 'line_ids': line_ids}
            self.env['b2b.business.items'].create(values)


class MRPBOM(models.Model):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'

    bom_type = fields.Selection(string="نوع جدول الكميات", selection=[('costing', 'Costing'), ('budgeting', 'Budgeting'), ], default='costing', )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="مشاريع المقاولات", required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="العملة", required=False,
                                  default=lambda self: self.env.user.company_id.currency_id)
    estimated_cost = fields.Monetary(string="التكلفة التقديرية", currency_field="currency_id", compute="_compute_estimated_cost", )

    
    @api.depends('bom_line_ids')
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = sum(rec.bom_line_ids.mapped('cost'))


class MRPBOMLines(models.Model):
    _name = 'mrp.bom.line'
    _inherit = 'mrp.bom.line'

    currency_id = fields.Many2one(comodel_name="res.currency", string="العملة",
                                  default=lambda self: self.env.user.company_id.currency_id)
    product_cost = fields.Monetary(string="تكلفة البند", currency_field="currency_id", required=False, )
    supplier_discount = fields.Float(string="خصم المورد (%)", required=False, )
    sales_tax = fields.Float(string="ضريبة المبيعات (%)", required=False, )
    customs = fields.Float(string="الجمارك (%)", required=False, )
    clearance = fields.Float(string="نسبة التخليص (%)", required=False, )
    product_price = fields.Monetary(string="سعر المنتج", currency_field="currency_id",
                                    compute="_compute_product_price", store=True)
    cost_after_discount = fields.Monetary(string="التكلفة بعد الخصم", currency_field="currency_id",
                                          compute="_compute_product_price", store=True)
    hockup = fields.Monetary(string="تكلفة الربط", currency_field="currency_id", required=False, )
    labor_install = fields.Monetary(string="تركيب العمالة", currency_field="currency_id", required=False, )
    transportation = fields.Monetary(string="النقل", currency_field="currency_id", required=False, )
    other_cost = fields.Monetary(string="تكلفة أخرى", currency_field="currency_id", required=False, )
    cost = fields.Monetary(string="إجمالي التكلفة", currency_field="currency_id", compute='_compute_cost', store=True)
    bom_type = fields.Selection(related="bom_id.bom_type", store=True)
    subtotal = fields.Monetary(string="الإجمالي", currency_field="currency_id", compute="_compute_cost", )
    product_id = fields.Many2one(
        'product.product', 'Component', domain=[('constration_product', '=', False)],  required=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
        return {'domain': {'product_id': [('constration_product', '=', False)]}}

    
    def create_pr(self):
        receive_order_user_vals = [(0, 0, {'product_id': self.product_id.id, 'unit_cost': self.cost, 'order_qty': self.product_qty})]
        construction_receive_order_obj = self.env['construction.receive.order'].create({'project_id': self.bom_id.construction_project_id.id,
                                                                                        'receive_order_user_ids': receive_order_user_vals})
        construction_receive_order_obj.name = "%s/pr%s" % (construction_receive_order_obj.project_id.code, self.env['ir.sequence'].next_by_code('construction.receive.order'))

    
    def create_mo(self):
        if not all([self.product_id.bom_ids, any([bom.active for bom in self.product_id.bom_ids]), any([bom.type == 'normal' for bom in self.product_id.bom_ids])]):
            raise UserError(_("%s is not valid for MO!\nCreate a valid Bill of Material for this product." % self.product_id.name))
        else:
            self.env['mrp.production'].create({'product_id': self.product_id.id, 'product_uom_id': self.product_id.uom_id.id})

    @api.depends('product_cost', 'supplier_discount', 'sales_tax', 'clearance', 'customs')
    def _compute_product_price(self):
        for rec in self:
            rec.cost_after_discount = rec.product_cost * (1 - rec.supplier_discount / 100)
            rec.product_price = rec.cost_after_discount * (1 + (rec.customs + rec.clearance + rec.sales_tax) / 100)

    @api.onchange('product_qty')
    @api.depends('product_price', 'hockup', 'labor_install', 'transportation', 'other_cost')
    def _compute_cost(self):
        for rec in self:
            rec.cost = (rec.product_price + rec.hockup + rec.labor_install + rec.transportation + rec.other_cost) * rec.product_qty
            rec.subtotal = rec.cost * rec.product_qty
    @api.onchange('name')
    def _onchange_product_name(self):
        self.uom_id = self.name.uom_id.id
        self.product_cost = self.name.standard_price


class ConstructionProject(models.Model):
    _name = 'construction.project'
    _inherit = 'construction.project'

    code = fields.Char(string="الكود", required=False, )
    bom_ids = fields.One2many(comodel_name="mrp.bom", inverse_name="construction_project_id", string="قوائم المواد", required=False, )
    bom_count = fields.Integer(string="قوائم المواد", compute="_compute_bom_count")

    
    @api.depends('bom_count')
    def _compute_bom_count(self):
        for rec in self:
            rec.bom_count = len([bom for bom in rec.bom_ids if bom.bom_type == 'budgeting'])
