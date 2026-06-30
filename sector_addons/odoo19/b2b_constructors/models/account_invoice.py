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
    quotation_ids = fields.One2many('invoice.quotation.lines', 'invoice_id',string='بنود عروض المقاولات')

class InvoiceQuatationLines(models.Model):
    _name = 'invoice.quotation.lines'


    _rec_name = "invoice_id"

    invoice_id = fields.Many2one("account.move", sring="Construction Qoutation", required=False)
    # purchase_order_id = fields.Many2one(related="progress_bill_id.purchase_order_id", string="جدول كميات المقاولات", readonly=False, store=True)
    # project_id = fields.Many2one(related="progress_bill_id.project_id", string='اسم المشروع', readonly=False, store=True)
    # consructor_id = fields.Many2one(related="progress_bill_id.consructor_id", string='المقاول', readonly=False)
    entrepreneurs_id = fields.Many2one("b2b.entrepreneurs", string="بيان الأعمال", required=False, readonly=False)
    # indexation_id = fields.Many2one(related="entrepreneurs_id.indexation_id",  string="بيان الأعمال", required=True, readonly=False)
    main_item_id = fields.Many2one("b2b.main.items", string="????? ???????", required=True, readonly=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="????? ??????", required=True, readonly=False)
    # business_statement_id = fields.Many2one(related="entrepreneurs_id.business_statement_id", string="بيان الأعمال", required=False, readonly=False, store=True)
    uom_id = fields.Many2one('uom.uom', string="الوحدة", readonly=False, store=True)
    required_quantity = fields.Float( string="الكمية المسندة", readonly=False)
    category = fields.Float( string="التصنيف", readonly=False,digits='Constructor price')

    previous_work = fields.Float( string="الأعمال السابقة")
    current_work = fields.Float(string="الأعمال الحالية")
    total_work = fields.Float( string="إجمالي الأعمال")
    work_amount = fields.Float( string="???? ???????")
    notes = fields.Text( string="ملاحظات", )
    perc_c = fields.Float( string="نسبة الإنجاز %", readonly=False)
