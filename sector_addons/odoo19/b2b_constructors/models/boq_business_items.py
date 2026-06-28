# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api, _


class BoqBusinessItemLine(models.Model):
    _name = 'b2b.business.item.line'

    name = fields.Many2one(comodel_name="product.product", string="Component", required=True, )
    business_item_id = fields.Many2one(comodel_name="b2b.business.items", string="Business Item", required=True, )
    uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", required=False, )
    qty = fields.Float(string="Quantity",  required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    cost = fields.Monetary(string="Cost", currency_field='currency_id')
    margin = fields.Float(string="Margin",  required=False)
    selling_price = fields.Monetary(string="Selling Price", currency_field='currency_id', compute="compute_selling_price")
    total_selling_price = fields.Monetary(string="Total Selling Price", currency_field='currency_id', compute="compute_total_selling_price")
    subtotal = fields.Monetary(string="Total Estimated Cost", currency_field='currency_id', required=False, compute='_compute_subtotal')

    @api.depends('selling_price', 'qty')
    def compute_total_selling_price(self):
        for rec in self:
            rec.total_selling_price = rec.qty * rec.selling_price

    @api.depends('cost', 'margin')
    def compute_selling_price(self):
        for rec in self:
            rec.selling_price = (rec.cost * rec.margin / 100) + rec.cost
    
    @api.depends('cost', 'qty')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.cost * rec.qty

    @api.onchange('name')
    def _onchange_name(self):
        for rec in self:
            rec.uom_id = rec.name.uom_id.id


class BoqBusinessItem(models.Model):
    _name = 'b2b.business.items'
    _inherit = ['mail.thread']
    _description = "BOQ Business Items"

    name = fields.Char(string="Title", required=True)
    sub_item_id = fields.Many2one("b2b.sub.items",related="sub_business_statement_id.sub_item_id", string="Sub Item", required=True)
    main_item_id = fields.Many2one(related="sub_business_statement_id.main_item_id", string="Main Item", readonly=True, store=True)
    uom_id = fields.Many2one("uom.uom", string="Unit", required=True)
    code = fields.Char()
    type_ids = fields.Many2many(comodel_name="b2b.business.items.type", relation="business_items_type_rel",
                                column1="item_id", column2="type_id", string="Types")
    sub_business_statement_id = fields.Many2one(
        'b2b.sub.business.items'
    )
    line_ids = fields.One2many(comodel_name="b2b.business.item.line", inverse_name="business_item_id", string="Item Lines", required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    estimated_cost = fields.Monetary(string="Estimated Cost", currency_field='currency_id', compute="_compute_estimated_cost")
    set_lines_readonly = fields.Boolean(string="Set Lines Readonly", compute="_compute_set_lines_readonly")
    creation_date = fields.Date(string="Creation Date", required=True)
    group_code = fields.Char("Code", compute="_compute_group_code")
    analytic_tags_ids = fields.Many2many(comodel_name="account.analytic.tag", relation="business_item_analytic_tags_rel", column1="business_item_id", column2="analytic_tag_id", string="Analytic Tags")

    @api.model
    def create(self, vals):
        print(vals)
        res = super(BoqBusinessItem, self).create(vals)
        return res

    @api.depends('sub_business_statement_id', 'sub_item_id', 'main_item_id', 'code')
    def _compute_group_code(self):
        for rec in self:
            code = ''
            if rec.main_item_id:
                code += rec.main_item_id.code
            if rec.sub_item_id:
                code += rec.sub_item_id.code
            if rec.sub_business_statement_id:
                code += rec.sub_business_statement_id.code
            if rec.code:
                code += rec.code
            rec.group_code = code
    
    @api.depends()
    def _compute_set_lines_readonly(self):
        construction_boq = self.env['b2b.construction.boq'].search([('state', 'in', ['wait_assignment', 'assigned'])])
        indexations = [con_boq.indexation_ids for con_boq in construction_boq if con_boq.indexation_ids]
        business_statement = []
        for ind in indexations:
            for i in ind:
                business_statement.append(i.business_statement_id.id)
        business_statement_ids = list(set(business_statement))

        if self.env.user.has_group('b2b_constructors.group_edit_business_statement_item') or self.id not in business_statement_ids:
            self.set_lines_readonly = False
        else:
            self.set_lines_readonly = True

    @api.depends('line_ids')
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = sum([l.subtotal for l in rec.line_ids])

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ Override name_search to change search name """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('group_code', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    def action_view_purchase_order_line(self):
        self.ensure_one()
        return {
            'name': _('Purchase Order Lines'),
            'view_mode': 'list,form',
            'res_model': 'purchase.order.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('order_id.state', '=', 'purchase'), ('business_item_id', '=', self.id)],
        }

    def action_view_stock_move(self):
        self.ensure_one()
        return {
            'name': _('Purchase Order Lines'),
            'view_mode': 'list,form',
            'res_model': 'stock.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('picking_id.state', 'not in', ['draft', 'cancel']), ('business_item_id', '=', self.id)],
        }
    

class BoqBusinessItemType(models.Model):
    _name = 'b2b.business.items.type'
    _rec_name = 'name'

    name = fields.Char()
