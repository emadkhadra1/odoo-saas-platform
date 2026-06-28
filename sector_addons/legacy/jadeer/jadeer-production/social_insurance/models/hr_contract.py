from odoo import models, fields, api


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    is_insured = fields.Boolean(default=False)
    social_insurance_number = fields.Char()
    basic_insurance_amount = fields.Integer()
    basic_insurance_salary = fields.Monetary(string="Basic Insurance Salary",compute="compute_basic_insurance_salary",
                                            inverse="set_basic_insurance_salary",readonly=False,store=True)
    variable_insurance_salary = fields.Monetary(string="Variable Insurance Salary")
    additional_salary = fields.Monetary(string="Additional Salary")
    employee_share_basic = fields.Monetary(string="Employee Share Basic", compute='_compute_employee_share_basic')
    employee_share_variable = fields.Monetary(string="Employee Share Variable",
                                              compute='_compute_employee_share_variable')
    company_share_basic = fields.Monetary(string="Company Share Basic", compute='_compute_company_share_basic')
    company_share_variable = fields.Monetary(string="Company Share Variable",
                                             compute='_compute_company_share_variable')
    employee_share_insurance = fields.Monetary(string="Employee Share Insurance",
                                               compute='_compute_employee_share_insurance')
    company_share_insurance = fields.Monetary(string="Company Share Insurance",
                                              compute='_compute_company_share_insurance')
    social_insurance = fields.Many2one(comodel_name="social.insurance", compute='_compute_social_insurance')
    gross_salary = fields.Monetary(string='Gross Salary',track_visibility='onchange',)
    net_salary = fields.Monetary(string='Total Salary')
    basic_salary = fields.Monetary(string="Basic", required=False, )
    social_insurance_salary = fields.Monetary(string="Social Insurance", required=False, )
    medical_insurance_salary = fields.Monetary(string="Medical Insurance", required=False, )
    car_allowance = fields.Monetary(string="Car Allowance")
    mobile_allowance = fields.Monetary(string="Mobile Allowance")
    transport_allowance = fields.Monetary(string="Transportation Allowance")
    bonus_allowance = fields.Monetary(string="Bonus Allowance")
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ])
    loan_other_insurance = fields.Monetary(string="Loan Other Insurance Members", required=False, )
    purchase_period = fields.Monetary(string="Purchase Period" )
    housing_allowance = fields.Monetary(string="Old Social Increment")
    transfer_allowance = fields.Monetary(string="New Social Increment.")
    other_allowance = fields.Monetary(string="May 99 LE")
    statue = fields.Selection([
        ('in', 'Insured'),
        ('out', 'Outsource'),
    ])
    insurance_start_date = fields.Date()
    varaible_insurance_amount = fields.Integer()
    age_above_60 = fields.Boolean(string="",  )
    retirement_salary = fields.Monetary(string="Retirement Salary")
    retirement_percentage_id = fields.Many2one(comodel_name="retirement.percentage",string="Employee %")
    # employee_percentage = fields.Monetary(string="Employee %")
    employee_share = fields.Monetary(string="Employee Share",compute="compute_employee_share",store=True)
    school_percentage = fields.Monetary(string="Company %")
    school_share = fields.Monetary(string="Company Share",compute="compute_school_share",store=True)


    @api.onchange('retirement_percentage_id')
    def onchange_retirement_percentage_id(self):
        self.school_percentage = self.retirement_percentage_id.school_percentage

    @api.depends('retirement_salary','retirement_percentage_id',
                 'retirement_percentage_id.employee_percentage')
    def compute_employee_share(self):
        for rec in self:
            rec.employee_share = rec.retirement_salary * rec.retirement_percentage_id.employee_percentage / 100

    @api.depends('retirement_salary','school_percentage')
    def compute_school_share(self):
        for rec in self:
            rec.school_share = rec.retirement_salary * rec.school_percentage / 100

    @api.depends('basic_salary','social_insurance.employee_min_limit_basic','wage',
                 'social_insurance.employee_min_limit_basic','is_insured')
    def compute_basic_insurance_salary(self):
        for rec in self:
            basic_insurance_salary = 0
            if rec.is_insured == True:
                if rec.wage < rec.social_insurance.employee_min_limit_basic:
                    basic_insurance_salary = rec.social_insurance.employee_min_limit_basic
                if rec.wage > rec.social_insurance.employee_max_limit_basic:
                    basic_insurance_salary = rec.social_insurance.employee_max_limit_basic

            rec.basic_insurance_salary = basic_insurance_salary

    def set_basic_insurance_salary(self):
        print("Set basic_insurance_salary")

    @api.depends('social_insurance.employee_basic')
    def _compute_employee_share_basic(self):
        for line in self:
            if line.is_insured == True:
                share_basic = line.social_insurance.employee_basic * line.basic_insurance_salary / 100
                line.employee_share_basic = share_basic
            else:
                line.employee_share_basic = 0

    @api.depends('social_insurance.employee_variable')
    def _compute_employee_share_variable(self):
        for line in self:
            if line.is_insured == True:
                share_variable = line.social_insurance.employee_variable * line.variable_insurance_salary / 100
                line.employee_share_variable = share_variable
            else:
                line.employee_share_variable = 0

    @api.depends('social_insurance.company_basic')
    def _compute_company_share_basic(self):
        for line in self:
            if line.is_insured == True:
                company_share_basic = line.social_insurance.company_basic * line.basic_insurance_salary / 100
                line.company_share_basic = company_share_basic
            else:
                line.company_share_basic = 0

    @api.depends('social_insurance.company_variable', 'variable_insurance_salary')
    def _compute_company_share_variable(self):
        for line in self:
            if line.is_insured == True:
                company_share_variable = line.social_insurance.company_variable * line.variable_insurance_salary / 100
                line.company_share_variable = company_share_variable
            else:
                line.company_share_variable = 0

    @api.depends('employee_share_basic', 'employee_share_variable')
    def _compute_employee_share_insurance(self):
        for line in self:
            if line.is_insured == True:
                employee_share_variable_total = line.employee_share_basic + line.employee_share_variable
                line.employee_share_insurance = employee_share_variable_total
            else:
                line.employee_share_insurance = 0

    @api.depends('company_share_basic', 'company_share_variable')
    def _compute_company_share_insurance(self):
        for line in self:
            if line.is_insured == True:
                company_share_variable_total = line.company_share_basic + line.company_share_variable
                line.company_share_insurance = company_share_variable_total
            else:
                line.company_share_insurance = 0

    def _compute_social_insurance(self):
        for rec in self:
            if rec.age_above_60:
                social_insurance = self.env['social.insurance'].search(
                    [('company_id', '=', rec.company_id.id),('age_above_60','=',True)], limit=1)
                rec.social_insurance = social_insurance.id
            else:
                social_insurance = self.env['social.insurance'].search(
                    [('company_id', '=', rec.company_id.id)],limit=1)
                rec.social_insurance = social_insurance.id
