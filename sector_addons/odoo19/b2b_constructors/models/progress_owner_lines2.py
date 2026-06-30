# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ProgressOwnerLines2(models.Model):
    _name = 'b2b.progress.owner.lines2'

    _description = "عرض المالك بدون بنود جدول الكميات"

    _rec_name = "progress_bill_id"

    progress_bill_id = fields.Many2one("b2b.progress.owner", sring="Construction Qoutation", required=True, ondelete='cascade',)
    #project_id = fields.Many2one("construction.project", string='اسم المشروع')
    project_id = fields.Many2one(related="progress_bill_id.project_id", string='اسم المشروع', readonly=True, store=True)
    consructor_id = fields.Many2one("res.partner", string='المقاول', required=False, domain="[('is_constructors', '=', True)]", context="{'default_is_constructors': True}")
    main_item_id = fields.Many2one("b2b.main.items", string="????? ???????", required=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="????? ??????", required=False )
    business_statement_id = fields.Many2one("b2b.business.items", string="بيان الأعمال", required=True)
    sub_business_statement_id = fields.Many2one("b2b.sub.business.items",string="????? ?????? ??????", required=True)
    uom_id = fields.Many2one(related="business_statement_id.uom_id", string="الوحدة", readonly=True)
    required_quantity = fields.Float(string="الكمية المسندة", required=True)
    category = fields.Float(string="التصنيف", required=True,digits='Constructor price')
    previous_work = fields.Float(string="الأعمال السابقة")
    current_work = fields.Float(string="الأعمال الحالية")
    total_work = fields.Float(compute="_calculate_fields", string="إجمالي الأعمال")
    work_amount = fields.Float(compute="_calculate_fields", string="???? ???????",digits='Constructor price')

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
            return {'domain':{'business_statement_id': [('sub_item_id', '=', self.sub_item_id.id)]}}
        else:
            return {'domain':{'business_statement_id': []}}

    @api.onchange('business_statement_id')
    def onchange_business_statement_id(self):
        for rec in self:
            if rec.business_statement_id:
                rec.sub_business_statement_id = rec.business_statement_id.sub_business_statement_id
                rec.sub_item_id = rec.business_statement_id.sub_item_id
                rec.main_item_id = rec.business_statement_id.sub_item_id.main_item_id

    
    @api.onchange('previous_work', 'current_work', 'category')
    @api.depends('previous_work', 'current_work', 'category')
    def _calculate_fields(self):
        for rec in self:
            rec.total_work = rec.previous_work + rec.current_work
            rec.work_amount = rec.current_work * rec.category
