# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api

class ConstructionType(models.Model):
    _name = 'b2b.progress.bill.type'

    _description = "Qoutation Type"

    name = fields.Char(string="Title", required=True)

    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
        "This Data found!"),]
