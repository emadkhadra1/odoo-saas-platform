from odoo import models, fields, api


class construction_labor(models.Model):
    _inherit = 'construction.labor'

    boq_id = fields.Many2one(comodel_name="b2b.construction.boq", tracking=True, string="جدول الكميات",
                             required=True, domain="[('project_id', '=', project_id)]")
    business_item_ids = fields.Many2many(comodel_name="b2b.business.items", compute="compute_business_item_ids")
    business_item_id = fields.Many2one(comodel_name="b2b.business.items", tracking=True,
                                       string="بند أعمال", domain="[('id', 'in', business_item_ids)]")

    @api.depends('boq_id')
    def compute_business_item_ids(self):
        for rec in self:
            rec.business_item_ids = rec.boq_id.indexation_ids.mapped('business_statement_id').ids if rec.boq_id else False


class ConstructionLaborLine(models.Model):
    _inherit = 'construction.labor.line'

    labor_install = fields.Float(string="تركيب العمالة", compute="compute_labour_install")

    @api.depends('order_labor_id.business_item_id')
    def compute_labour_install(self):
        for rec in self:
            rec.labor_install = sum(lab.labor_install for lab in rec.order_labor_id.business_item_id.line_ids)
