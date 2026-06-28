# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import ValidationError, UserError

class ProductHistory(models.Model):
    _name = 'product.history'

    state = fields.Selection([
        ('replace', 'Replace'),
        ('waiver', 'Cede'),
        ('sold', 'Sold'),
        ('hold', 'Hold'),
        ('booked', 'Booked'),
        ('blocked', 'Blocked'),
        ('sale', 'Back For Sale'),
        ('hold_approve', 'Hold Approve'),
        ('hold_rejected', 'Hold Rejected'),
        ('recovery', 'Return'),
        ('update_price', 'Update Price'),
    ], string='Status', readonly=True, required=True, copy=False, index=True)
    hist_date = fields.Datetime(string='Actual Date')
    confirm_date = fields.Datetime(string='Contract Date', readonly=True)
    attachment_id = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                     'Attachments', store=True)
    product_id = fields.Many2one('product.template')
    sales_person_id = fields.Many2one('res.users', string='Responsible', readonly=True,
                                      default=lambda self: self.env.user)

    actual_price = fields.Float(string="Actual Price")
    updated_price = fields.Float(string="Updated Price")

