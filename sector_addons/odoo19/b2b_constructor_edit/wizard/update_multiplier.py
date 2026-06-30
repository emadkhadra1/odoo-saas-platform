from odoo import api, fields, models


class UpdateMultiplier(models.TransientModel):
    _name = 'update.multiplier'
    _rec_name = 'name'
    _description = 'تحديث المعامل'

    multiplier = fields.Float(string="المعامل", )
    discount = fields.Float(string="الخصم (%)", required=False, )
    social_insurance = fields.Float(string="التأمينات الاجتماعية (%)", required=False, )
    contracting = fields.Float(string="نسبة المقاولة (%)", required=False, )
    name = fields.Many2one(comodel_name="b2b.construction.boq", string="جدول كميات المقاولات", required=False, )

    def update_multiplier_default_value(self):
        self.name.multiplier = self.multiplier

    def update_lines_multiplier(self):
        indexation_ids = self.name.indexation_ids.search([('purchase_order_id', '=', self.name.id)])
        for index in indexation_ids:
            index.write({'multiplier': self.multiplier})
            index._onchnage_calculation_values()

    def update_discount_default_value(self):
        self.name.discount = self.discount

    def update_lines_discount(self):
        indexation_ids = self.name.indexation_ids.search([('purchase_order_id', '=', self.name.id)])
        for index in indexation_ids:
            index.write({'discount': self.discount})
            index._onchnage_calculation_values()

    def update_social_insurance_default_value(self):
        self.name.social_insurance = self.social_insurance

    def update_lines_social_insurance(self):
        indexation_ids = self.name.indexation_ids.search([('purchase_order_id', '=', self.name.id)])
        for index in indexation_ids:
            index.write({'social_insurance': self.social_insurance})
            index._onchnage_calculation_values()

    def update_contracting_default_value(self):
        self.name.contracting = self.contracting

    def update_lines_contracting(self):
        indexation_ids = self.name.indexation_ids.search([('purchase_order_id', '=', self.name.id)])
        for index in indexation_ids:
            index.write({'contracting': self.contracting})
            index._onchnage_calculation_values()
