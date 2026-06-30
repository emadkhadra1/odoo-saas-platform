# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class Indexation(models.Model):
    _name = 'b2b.indexation'
    _inherit = ['mail.thread']
    _description = "بنود جدول الكميات"

    _rec_name = "business_statement_id"

    purchase_order_id = fields.Many2one("b2b.construction.boq", string="جدول كميات المقاولات", required=True, ondelete='cascade',)
    main_item_id = fields.Many2one("b2b.main.items", string="????? ???????", required=True)
    sub_item_id = fields.Many2one("b2b.sub.items", string="????? ??????", required=True )
    business_statement_id = fields.Many2one("b2b.business.items", string="بيان الأعمال", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="العملة",
                                  default=lambda self: self.env.user.company_id.currency_id)
    cost = fields.Monetary(related='business_statement_id.estimated_cost', store=True)
    sub_business_statement_id = fields.Many2one("b2b.sub.business.items", string="????? ?????? ??????", required=True)
    uom_id = fields.Many2one(related="business_statement_id.uom_id", string="الوحدة", readonly=True, store=True)
    category = fields.Float(string="التصنيف",digits='Constructor price')
    required_quantity = fields.Float(string="الكمية المطلوبة")
    finished_quantity = fields.Float(compute="_calculate_quantity", string="الكمية المنجزة")
    remaining_quantity = fields.Float(compute="_calculate_quantity", string="الكمية المتبقية")
    total = fields.Float(compute="_calculate_quantity", string="إجمالي البيع")
    total_cost = fields.Float(compute="_calculate_quantity", string="إجمالي التكلفة")

    @api.onchange('main_item_id')
    def onchange_main_item_id(self):
        if self.main_item_id:
            return {'domain':{'sub_item_id': [('main_item_id', '=', self.main_item_id.id)]}}
        else:
            return {'domain':{'sub_item_id': []}}

    @api.onchange('sub_item_id')
    def onchange_sub_item_id(self):
        if self.sub_item_id:
            self.main_item_id = self.sub_item_id.main_item_id.id
            return {'domain':{'business_statement_id': [('sub_item_id', '=', self.sub_item_id.id)]}}
        else:
            return {'domain':{'business_statement_id': []}}

    @api.onchange('business_statement_id')
    def onchange_business_statement_id(self):
        for rec in self:
            if rec.business_statement_id:
                rec.sub_business_statement_id = rec.business_statement_id.sub_business_statement_id
                rec.sub_item_id = rec.business_statement_id.sub_item_id
                rec.main_item_id = rec.business_statement_id.sub_item_id.main_item_id

    
    @api.depends('required_quantity', 'التكلفة', 'category')
    def _calculate_quantity(self):
        bill_lines = self.env["b2b.progress.bill.lines"]
        for rec in self:
            finished = 0.0
            remaining = 0.0
            if rec.required_quantity:
                quotations = bill_lines.search([
                    ("business_statement_id", "=", rec.business_statement_id.id),
                ])
                for s in quotations:
                    finished += s.current_work
                remaining = rec.required_quantity - finished
            rec.finished_quantity = finished
            rec.remaining_quantity = remaining
            rec.total =rec.category * rec.required_quantity
            rec.total_cost =rec.cost * rec.required_quantity
