from odoo import api, fields, models


class EmployeeReport(models.AbstractModel):
    _inherit = 'hr.employee.base'

    num_insurance_years = fields.Integer(string="Years No.", required=False, )
    num_insurance_months = fields.Integer(string="Months No.", required=False, )


class Employee(models.Model):
    _inherit = 'hr.employee'

    is_insured = fields.Boolean(related="contract_id.is_insured")
    social_insurance_number = fields.Char(related="contract_id.social_insurance_number")
    statue = fields.Selection(related="contract_id.statue")
    insurance_start_date = fields.Date(related="contract_id.insurance_start_date")
    num_insurance_years = fields.Integer(string="Years No.", required=False, )
    num_insurance_months = fields.Integer(string="Months No.", required=False, )
    total_insurance_years = fields.Integer(compute="compute_total_insurance_duration")
    total_insurance_months = fields.Integer(compute="compute_total_insurance_duration")

    @api.depends("num_insurance_years",'num_insurance_months','contract_id.insurance_start_date')
    def compute_total_insurance_duration(self):
        for rec in self:
             total_months = rec.num_insurance_months
             total_years = rec.num_insurance_years
             if rec.contract_id.insurance_start_date:
                diff = fields.date.today() - rec.contract_id.insurance_start_date
                year = int(diff.days / 365)
                days = diff.days % 365
                months = int(days / 30)
                total_months += months
                if total_months > 11:
                    year += int(total_months / 12)
                    total_months = total_months % 12
                total_years += year
             rec.total_insurance_months = total_months
             rec.total_insurance_years = total_years


