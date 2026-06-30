# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsignmentConstructorWizard(models.TransientModel):
    _name = 'b2b.entrepreneurs.wizard'

    _description = "المقاولون المسندون"

    _rec_name = "purchase_order_id"

    def _get_purchase_order_id(self):
        return self._context.get('active_id') if self._context.get('active_id') else None

    def _get_business_items_ids(self):
        if self._context.get('active_id'):
            order = self.env['b2b.construction.boq'].search([('id', '=', self._context.get('active_id'))])
            return order.indexation_ids.mapped('business_statement_id')

    def _get_sub_item_ids(self):
        if self._context.get('active_id'):
            order = self.env['b2b.construction.boq'].search([('id', '=', self._context.get('active_id'))])
            return order.indexation_ids.mapped('sub_item_id')

    def _get_main_item_ids(self):
        if self._context.get('active_id'):
            order = self.env['b2b.construction.boq'].search([('id', '=', self._context.get('active_id'))])
            return order.indexation_ids.mapped('main_item_id')

    # def _get_sub_business_statement_ids(self):
    #     if self._context.get('active_id'):
    #         order = self.env['b2b.construction.boq'].search([('id', '=', self._context.get('active_id'))])
    #         return order.indexation_ids.mapped('sub_business_statement_id')

    purchase_order_id = fields.Many2one("b2b.construction.boq", string="جدول كميات المقاولات", required=True, ondelete='cascade', readonly=True, default=_get_purchase_order_id)
    sub_business_statement_id = fields.Many2one("b2b.sub.business.items", string="????? ?????? ??????", required=False )
    # sub_business_statement_ids = fields.Many2one("b2b.sub.business.items",
    #                                              default=_get_sub_business_statement_ids,readonly=1,
    #                                              string="????? ?????? ??????", required=False )
    consructor_id = fields.Many2one("res.partner", string='المقاول', required=True, domain="[('is_constructors', '=', True)]", context="{'default_is_constructors': True}")
    main_item_id = fields.Many2one("b2b.main.items", string="????? ???????", required=False)
    main_item_ids = fields.Many2many("b2b.main.items",
                                     default=_get_main_item_ids,readonly=1,
                                     string="????? ???????", required=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="????? ??????", required=False )
    sub_item_ids = fields.Many2many("b2b.sub.items", string="????? ??????",
                                    default=_get_sub_item_ids,readonly=1
                                    ,required=False )
    business_items_ids = fields.Many2many(
        'b2b.business.items',readonly=1,
        default=_get_business_items_ids
    )
    business_statement_id = fields.Many2one("b2b.business.items",
                                            string="بيان الأعمال", required=False)
    percent = fields.Float(string="النسبة", required=False, default=100)
    item_ids = fields.One2many('b2b.assign.items.wizard', 'entrepreneurs_id', string='??????', required=True)
    # indexation_id = fields.Many2one("b2b.indexation", string='بند جدول الكميات', required=True, domain="[('purchase_order_id', '=', purchase_order_id)]", context="{'default_purchase_order_id': purchase_order_id}")

    
    @api.onchange('consructor_id', 'item_ids')
    def onchange_consructor_id(self):
        for rec in self:
            for line in rec.item_ids:
                if rec.consructor_id:
                    line.consructor_id = rec.consructor_id

    
    @api.onchange('purchase_order_id')
    def onchange_purchase_order_id(self):
        for rec in self:
            main_items = [x.main_item_id.id for x in rec.purchase_order_id.indexation_ids]
            sub_items = [x.sub_item_id.id for x in rec.purchase_order_id.indexation_ids]
            business_items = [x.business_statement_id.id for x in rec.purchase_order_id.indexation_ids]

            return {
                'domain':{
                    'main_item_id': [('id', 'in', main_items)],
                    'sub_item_id': [('id', 'in', sub_items)],
                    'business_statement_id': [('id', 'in', business_items)],
                    },
                }

    @api.onchange('main_item_id')
    def onchange_main_item_id(self):
        self.sub_item_id = None
        self.business_statement_id = None
        self.item_ids = None

        indexations = self.env["b2b.indexation"].search([
            ("purchase_order_id", "=", self.purchase_order_id.id),
            ("main_item_id", "=", self.main_item_id.id),
        ])

        lines = []
        for line in indexations:
            lines.append((0, 0, {
                "indexation_id": line.id,
                "purchase_order_id": self.purchase_order_id.id,
                "consructor_id": self.consructor_id.id,
                "price": line.category,
            }))
        self.item_ids = lines


        if self.main_item_id:
            return {'domain':{
                'sub_item_id': [('main_item_id', '=', self.main_item_id.id)],
                'business_statement_id': [('sub_item_id.main_item_id', '=', self.main_item_id.id)]
                }}
        else:
            return {'domain':{
                'sub_item_id': [],
                'business_statement_id': []
                }}

    @api.onchange('sub_item_id')
    def onchange_sub_item_id(self):
        self.business_statement_id = None
        self.item_ids = None

        indexations = self.env["b2b.indexation"].search([
            ("purchase_order_id", "=", self.purchase_order_id.id),
            ("sub_item_id", "=", self.sub_item_id.id),
        ])

        lines = []
        for line in indexations:
            lines.append((0, 0, {
                "indexation_id": line.id,
                "purchase_order_id": self.purchase_order_id.id,
                "consructor_id": self.consructor_id.id,
                "price": line.category,
            }))

        self.item_ids = lines

        if self.sub_item_id:
            return {'domain':{'business_statement_id': [('sub_item_id', '=', self.sub_item_id.id)]}}
        else:
            return {'domain':{'business_statement_id': []}}

    @api.onchange('business_statement_id')
    @api.constrains('business_statement_id')
    def onchange_business_statement_id(self):
        self.item_ids = None

        if self.business_statement_id:
            indexations = self.env["b2b.indexation"].search([
                ("purchase_order_id", "=", self.purchase_order_id.id),
                ("business_statement_id", "=", self.business_statement_id.id),
            ])

            lines = []
            for line in indexations:
                lines.append((0, 0, {
                    "indexation_id": line.id,
                    "purchase_order_id": self.purchase_order_id.id,
                    "consructor_id": self.consructor_id.id,
                    "price": line.category,
                }))

                self.item_ids = lines

    
    def action_assign(self):
        entrep = self.env["b2b.entrepreneurs"].sudo()
        for rec in self:
            if rec.item_ids:
                for line in rec.item_ids:
                    entrep.create({
                        "purchase_order_id": line.purchase_order_id.id,
                        "consructor_id": line.consructor_id.id,
                        "indexation_id": line.indexation_id.id,
                        "price": line.price,
                        "percent": line.percent,
                        })
        return {'type': 'ir.actions.act_window_close'}
