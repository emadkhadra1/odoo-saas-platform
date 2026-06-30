# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class BoqSubBusinessStatement(models.Model):
    _name = 'b2b.sub.business.items'
    _rec_name = 'name'
    _description = "BOQ Second Sub Items"

    name = fields.Char(string="Title", required=True)
    sub_item_id = fields.Many2one("b2b.sub.items", string="البند الفرعي", store=True)
    main_item_id = fields.Many2one(related="sub_item_id.main_item_id", string="البند الرئيسي", readonly=True, store=True)
    # uom_id = fields.Many2one("uom.uom", string="Unit", required=True)
    code = fields.Char()
    group_code = fields.Char("Code", compute="_compute_group_code")

    @api.depends('sub_item_id', 'main_item_id', 'code')
    def _compute_group_code(self):
        for rec in self:
            code = ''
            if rec.main_item_id:
                code += rec.main_item_id.code
            if rec.sub_item_id:
                code += rec.sub_item_id.code
            if rec.code:
                code += rec.code
            rec.group_code = code

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ Override name_search to change search name """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('group_code', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()
