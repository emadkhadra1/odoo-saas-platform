# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class ConstructionType(models.Model):
    _name = 'b2b.constrution.type'

    _description = "أنواع المقاولات"

    name = fields.Char(string="العنوان", required=True)

    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
        "This Data found!"),]
