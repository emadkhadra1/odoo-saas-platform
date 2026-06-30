# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class BoqMainItems(models.Model):
    _name = 'b2b.main.items'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "BOQ Main Items"

    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
        "This data found!"),]

    name = fields.Char(string="Title", required=True)
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
