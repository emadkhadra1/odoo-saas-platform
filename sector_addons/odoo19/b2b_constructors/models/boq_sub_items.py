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

    _description = "البنود الفرعية في جدول الكميات"

    name = fields.Char(string="العنوان", required=True)
    main_item_id = fields.Many2one("b2b.main.items", string="????? ???????", required=True)
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
