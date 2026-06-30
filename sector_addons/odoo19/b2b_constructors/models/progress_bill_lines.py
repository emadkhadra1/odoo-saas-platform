# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ProgressBillLines(models.Model):
    _name = 'b2b.progress.bill.lines'

    _description = "عرض سعر مع بنود جدول الكميات"

    _rec_name = "progress_bill_id"

    progress_bill_id = fields.Many2one("b2b.progress.bill", sring="Construction Qoutation", required=False)
    purchase_order_id = fields.Many2one(related="progress_bill_id.purchase_order_id", string="جدول كميات المقاولات", readonly=False, store=True)
    project_id = fields.Many2one(related="progress_bill_id.project_id", string='اسم المشروع', readonly=False, store=True)
    consructor_id = fields.Many2one(related="progress_bill_id.consructor_id", string='المقاول', readonly=False, store=True)
    entrepreneurs_id = fields.Many2one("b2b.entrepreneurs", string="بيان الأعمال 0", required=False, readonly=False)
    indexation_id = fields.Many2one(related="entrepreneurs_id.indexation_id",  string="بيان الأعمال 1", required=True, readonly=False)
    main_item_id = fields.Many2one(related="entrepreneurs_id.main_item_id", string="????? ???????", required=True, readonly=False)
    sub_item_id = fields.Many2one(related="entrepreneurs_id.sub_item_id", string="????? ??????", required=True, readonly=False)
    business_statement_id = fields.Many2one(related="entrepreneurs_id.business_statement_id", string="بيان الأعمال 2", required=False, readonly=False, store=True)
    type_ids = fields.Many2many(related="business_statement_id.type_ids")
    type_id = fields.Many2one(comodel_name="b2b.business.items.type", string="النوع", required=False,
                              domain="[('id', 'in', type_ids)]")
    sub_business_statement_id = fields.Many2one(related="entrepreneurs_id.sub_business_statement_id", string="????? ?????? ??????", required=False, readonly=False, store=True)
    uom_id = fields.Many2one(related="indexation_id.uom_id", string="الوحدة", readonly=False, store=True)
    required_quantity = fields.Float(related="entrepreneurs_id.percent", string="الكمية المسندة", readonly=False)
    # category = fields.Float(related="indexation_id.category", string="التصنيف", readonly=False)
    # category = fields.Float( string="التصنيف", readonly=False,digits='Constructor price')
    category = fields.Float( string="التصنيف", related="entrepreneurs_id.price",readonly=False,digits='Constructor price')

    previous_work = fields.Float(compute="_calculate_fields", string="الأعمال السابقة")
    current_work = fields.Float(string="الأعمال الحالية")
    total_work = fields.Float(compute="_calculate_fields", string="إجمالي الأعمال", store=True)
    work_amount = fields.Float(compute="_calculate_fields", string="???? ???????", store=True,digits='Constructor price')
    notes = fields.Text( string="ملاحظات", )
    perc_c = fields.Float( string="نسبة الإنجاز %",default=100, readonly=False)

    
    # @api.onchange('business_statement_id', 'current_work')
    @api.depends('entrepreneurs_id', 'current_work','category','perc_c', 'business_statement_id')
    def _calculate_fields(self):
        for rec in self:
            previous = 0.0
            if rec.entrepreneurs_id:
                if not rec.progress_bill_id.purchase_order_id or not rec.progress_bill_id.project_id or not rec.progress_bill_id.consructor_id or not rec.progress_bill_id.from_date:

                    rec.business_statement_id = None
                    # raise ValidationError(_("???? ????? ???? ??????? ???? ??????? ???????? ?????? ??????? ??? ????? ???? ??? ?????."))
                else:
                    previous_data = self.search(
                        [
                            ("entrepreneurs_id", "=", rec.entrepreneurs_id.id),
                            # ("purchase_order_id", "=", rec.purchase_order_id.id),
                            # ("project_id", "=", rec.project_id.id),
                            # ("consructor_id", "=", rec.consructor_id.id),
                            # ("progress_bill_id.to_date", "<", rec.progress_bill_id.from_date),
                            ("progress_bill_id.state", "=", 'approve'),

                        ]
                    )
                    for s in previous_data:
                        if (isinstance(rec.id, int) and s.id != rec.id) or not isinstance(rec.id, int):
                            previous += s.current_work
            rec.previous_work = previous
            rec.total_work = previous + rec.current_work
            rec.work_amount = (rec.total_work * rec.category) * (rec.perc_c / 100)

    
    @api.onchange('entrepreneurs_id')
    def on_change_calculate_fields(self):
        for rec in self:
            previous = 0.0
            notes=''
            if  rec.entrepreneurs_id and rec.project_id:
                if  not rec.progress_bill_id.project_id or not rec.progress_bill_id.consructor_id or not rec.progress_bill_id.from_date:
                    rec.business_statement_id = None
                    raise ValidationError(_("???? ????? ???? ??????? ???? ??????? ???????? ?????? ??????? ??? ????? ???? ??? ?????."))
                else:
                    previous_data = self.search(
                        [
                            ("entrepreneurs_id", "=", rec.entrepreneurs_id.id),
                            # ("project_id", "=", rec.project_id.id),
                            # ("consructor_id", "=", rec.consructor_id.id),
                            # ("progress_bill_id.to_date", "<", rec.progress_bill_id.from_date),
                        ]
                    )
                    # ("purchase_order_id", "=", rec.purchase_order_id.id),

                    for s in previous_data:
                        if (isinstance(rec.id, int) and s.id != rec.id) or not isinstance(rec.id, int):
                            previous += s.current_work
                            if s.notes:
                                notes += s.notes + ' '

                    # rec.previous_work = previous
                    rec.notes = notes

                    # rec.total_work = previous + rec.current_work
                    # rec.work_amount = rec.current_work * rec.category
