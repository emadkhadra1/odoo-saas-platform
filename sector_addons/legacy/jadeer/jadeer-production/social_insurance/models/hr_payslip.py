from odoo import models, fields, api


class ContractInherit(models.Model):
    _inherit = 'hr.payslip'

    is_insured = fields.Boolean(default=False)

    basic_insurance_salary = fields.Monetary(string="Basic Insurance Salary")
    variable_insurance_salary = fields.Monetary(string="Variable Insurance Salary")
    employee_share_insurance = fields.Monetary(string="Employee Share Insurance")
    company_share_insurance = fields.Monetary(string="Company Share Insurance",)

    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def check_fields(self):
        for rec in self:
            if rec.employee_id:
                running_contract = rec.employee_id.contract_ids.filtered(lambda x:x.state=='open')
                if running_contract:
                    running_contract = running_contract[0]
                if running_contract and running_contract.is_insured:
                    rec.is_insured = True
                    rec.basic_insurance_salary = running_contract.basic_insurance_salary
                    rec.variable_insurance_salary = running_contract.variable_insurance_salary
                    rec.employee_share_insurance = running_contract.employee_share_insurance
                    rec.company_share_insurance = running_contract.company_share_insurance

