from odoo import api, fields, models, _


class SelectUnitWizardLine(models.TransientModel):
    _name = 'select.unit.wizard.line'

    unit_id = fields.Many2one(comodel_name="product.template", string="Unit",)
    list_price = fields.Float(related="unit_id.list_price")
    project_id = fields.Many2one(related="unit_id.project_id")
    total_Area = fields.Float(related="unit_id.total_Area")
    is_select = fields.Boolean(string="Select")
    select_wizard_id = fields.Many2one(comodel_name="select.unit.wizard")


class SelectUnitWizard(models.TransientModel):
    _name = 'select.unit.wizard'

    lead_id = fields.Many2one(comodel_name="crm.lead",)
    unit_ids = fields.One2many(comodel_name="select.unit.wizard.line",
                                    inverse_name="select_wizard_id",)

    @api.onchange('lead_id')
    @api.constrains('lead_id')
    def get_units(self):
        domain = self.lead_id.prepare_unit_search_domain()
        composite_domain = self.lead_id.prepare_compo_unit_search_domain()
        res = self.env['product.template'].search(domain)
        composite_res = self.env['product.template'].search(composite_domain)
        if self.lead_id.singularity_ids and res:
            res = res.filtered(
                lambda l: self.lead_id.singularity_ids in l.singularity_ids or self.lead_id.singularity_ids == l.singularity_ids)
        res |= composite_res
        units = self.env['product.template'].search([('id','in',res.ids)])
        unit_lst = []
        for unit in units:
            unit_lst.append((0,0,{'unit_id':unit.id}))
        self.unit_ids = unit_lst

    def confirm(self):
        selected_unit = self.unit_ids.filtered(lambda x: x.is_select)
        if selected_unit:
            self.lead_id.unit_id = selected_unit[0].unit_id.id
