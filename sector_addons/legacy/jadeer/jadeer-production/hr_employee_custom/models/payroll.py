from odoo import models, fields, api


class ContractInherit(models.Model):
    _inherit = 'hr.payslip'
    # @api.onchange('employee_id')
    # @api.constrains('employee_id')
    # def set_salary_struct(self):
    #     for rec in self:
    #         if rec.employee_id:
    #             if rec.employee_id.salary_structure_id:
    #                 rec.struct_id = rec.employee_id.salary_structure_id.id
