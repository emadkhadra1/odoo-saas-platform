# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ProgressOwnerLines(models.Model):
    _name = 'b2b.progress.owner.lines'

    _description = "Owner Qoutation With BOQ Lines"

    _rec_name = "progress_bill_id"

    progress_bill_id = fields.Many2one("b2b.progress.owner", sring="Construction Qoutation", required=False)
    purchase_order_id = fields.Many2one(related="progress_bill_id.purchase_order_id", string="Construction BOQ", readonly=False, store=True)
    project_id = fields.Many2one(related="progress_bill_id.project_id", string='Project Name', readonly=False, store=True)
    consructor_id = fields.Many2one(related="progress_bill_id.consructor_id", string='Constructor', readonly=False, store=True)
    entrepreneurs_id = fields.Many2one("b2b.entrepreneurs", string="Business Statement", required=False, readonly=False)
    indexation_id = fields.Many2one(related="entrepreneurs_id.indexation_id",  string="Business Statement", required=True, readonly=False)
    main_item_id = fields.Many2one("b2b.main.items", string="البند الرئيسي", required=True, readonly=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="البند الفرعي", required=True, readonly=False)
    business_statement_id = fields.Many2one("b2b.business.items", string="Business Statement", required=False, readonly=False, store=True)
    sub_business_statement_id = fields.Many2one("b2b.sub.business.items", string="البند الفرعي الثاني", required=False, readonly=False, store=True)
    uom_id = fields.Many2one('uom.uom', string="Unit", readonly=False, store=True)
    required_quantity = fields.Float(string="Assigned Quantity", related='indexation_id.required_quantity', readonly=False, store=True)

    category = fields.Float(string="Category", related='indexation_id.category', store=True)
    # category = fields.Float( string="Category", readonly=False,digits='Constructor price')

    previous_work = fields.Float(string="Previous Work", compute="on_change_calculate_fields")
    current_work = fields.Float(string="Current Work")
    total_work = fields.Float(compute="_calculate_fields", string="Total Work", store=True)
    work_amount = fields.Float(compute="_calculate_fields", string="قيمة الأعمال", store=True,digits='Constructor price')
    notes = fields.Text( string="Notes", compute="on_change_calculate_fields")
    perc_c = fields.Float( string="Percentage of completion %", readonly=False)

    # 
    # @api.onchange('category', 'current_work')
    # def _calculate_fields(self):
    
    # @api.onchange('business_statement_id', 'current_work')
    @api.depends('entrepreneurs_id', 'current_work','category','perc_c', 'current_work')
    def _calculate_fields(self):
        for rec in self:
            previous = 0.0
            notes=''
            total_work = 0.0
            work_amount = 0.0
            if rec.project_id:
                if  not rec.progress_bill_id.project_id or not rec.progress_bill_id.consructor_id or not rec.progress_bill_id.from_date:
                    rec.business_statement_id = None
                    raise ValidationError(_("يرجى تحديد جدول الكميات واسم المشروع والمقاول وتاريخ البداية قبل إضافة بنود عرض السعر."))
                else:
                    previous_data = self.search(
                        [
                            ("entrepreneurs_id", "=", rec.entrepreneurs_id.id),
                            ("project_id", "=", rec.project_id.id),
                            ("progress_bill_id.state", "=", 'approve'),
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

                    total_work = previous + rec.current_work
                    # rec.work_amount = rec.total_work * rec.category
                    work_amount = (total_work * rec.category) * (rec.perc_c / 100)
            rec.total_work = total_work
            rec.work_amount = work_amount

    
    @api.depends('entrepreneurs_id', 'current_work', 'category', 'required_quantity')
    def on_change_calculate_fields(self):
        for rec in self:
            previous = 0.0
            notes=''
            if  rec.entrepreneurs_id and rec.project_id:
                if  not rec.progress_bill_id.project_id or not rec.progress_bill_id.consructor_id or not rec.progress_bill_id.from_date:
                    rec.business_statement_id = None
                    raise ValidationError(_("يرجى تحديد جدول الكميات واسم المشروع والمقاول وتاريخ البداية قبل إضافة بنود عرض السعر."))
                else:
                    previous_data = self.search(
                        [
                            ("entrepreneurs_id", "=", rec.entrepreneurs_id.id),
                            ("project_id", "=", rec.project_id.id),
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

            rec.previous_work = previous
            rec.notes = notes

                    # rec.total_work = previous + rec.current_work
                    # rec.work_amount = rec.current_work * rec.category
    @api.onchange('main_item_id')
    def onchange_main_item_id(self):
        if self.main_item_id:
            return {'domain':{'sub_item_id': [('main_item_id', '=', self.main_item_id.id)]}}
        else:
            return {'domain':{'sub_item_id': []}}

    @api.onchange('sub_item_id')
    def onchange_sub_item_id(self):
        if self.sub_item_id:
            self.main_item_id = self.sub_item_id.main_item_id.id
            return {'domain':{'entrepreneurs_id': [('sub_item_id', '=', self.sub_item_id.id)]}}
        else:
            return {'domain':{'entrepreneurs_id': []}}
