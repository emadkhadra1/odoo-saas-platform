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
    _description = "Construction BOQ Lines"

    _rec_name = "business_statement_id"

    purchase_order_id = fields.Many2one("b2b.construction.boq", string="Construction BOQ", required=True, ondelete='cascade',)
    main_item_id = fields.Many2one("b2b.main.items", string="البند الرئيسي", required=True)
    sub_item_id = fields.Many2one("b2b.sub.items", string="البند الفرعي", required=True )
    business_statement_id = fields.Many2one("b2b.business.items", string="Business Statement", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    cost = fields.Monetary(related='business_statement_id.estimated_cost', store=True)
    sub_business_statement_id = fields.Many2one("b2b.sub.business.items", string="البند الفرعي الثاني", required=True)
    uom_id = fields.Many2one(related="business_statement_id.uom_id", string="Unit", readonly=True, store=True)
    category = fields.Float(string="Category",digits='Constructor price')
    required_quantity = fields.Float(string="Required Quantity")
    finished_quantity = fields.Float(compute="_calculate_quantity", string="Finished Quantity")
    remaining_quantity = fields.Float(compute="_calculate_quantity", string="Remaining Quantity")
    total = fields.Float(compute="_calculate_quantity", string="Total Sell")
    total_cost = fields.Float(compute="_calculate_quantity", string="Total Cost")

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

    
    @api.depends('required_quantity', 'cost', 'category')
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
