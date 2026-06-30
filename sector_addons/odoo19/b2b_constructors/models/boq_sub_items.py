# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class BoqSubItem(models.Model):
    _name = 'b2b.sub.items'
    _rec_name = 'name'

    _description = "BOQ Sub Items"

    name = fields.Char(string="Title", required=True)
    main_item_id = fields.Many2one("b2b.main.items", string="البند الرئيسي", required=True)
    code = fields.Char()

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ Override name_search to change search name """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()
