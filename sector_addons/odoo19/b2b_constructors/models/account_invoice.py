# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class Invoice(models.Model):
    _inherit = 'account.move'
    quotation_ids = fields.One2many('invoice.quotation.lines', 'invoice_id',string='Construction Quotation Lines')

class InvoiceQuatationLines(models.Model):
    _name = 'invoice.quotation.lines'


    _rec_name = "invoice_id"

    invoice_id = fields.Many2one("account.move", sring="Construction Qoutation", required=False)
    # purchase_order_id = fields.Many2one(related="progress_bill_id.purchase_order_id", string="Construction BOQ", readonly=False, store=True)
    # project_id = fields.Many2one(related="progress_bill_id.project_id", string='Project Name', readonly=False, store=True)
    # consructor_id = fields.Many2one(related="progress_bill_id.consructor_id", string='Constructor', readonly=False)
    entrepreneurs_id = fields.Many2one("b2b.entrepreneurs", string="Business Statement", required=False, readonly=False)
    # indexation_id = fields.Many2one(related="entrepreneurs_id.indexation_id",  string="Business Statement", required=True, readonly=False)
    main_item_id = fields.Many2one("b2b.main.items", string="البند الرئيسي", required=True, readonly=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="البند الفرعي", required=True, readonly=False)
    # business_statement_id = fields.Many2one(related="entrepreneurs_id.business_statement_id", string="Business Statement", required=False, readonly=False, store=True)
    uom_id = fields.Many2one('uom.uom', string="Unit", readonly=False, store=True)
    required_quantity = fields.Float( string="Assined Quantity", readonly=False)
    category = fields.Float( string="Category", readonly=False,digits='Constructor price')

    previous_work = fields.Float( string="Previous Work")
    current_work = fields.Float(string="Current Work")
    total_work = fields.Float( string="Total Work")
    work_amount = fields.Float( string="قيمة الأعمال")
    notes = fields.Text( string="Notes", )
    perc_c = fields.Float( string="Percentage of completion %", readonly=False)
