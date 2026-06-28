# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    payslip_tax_type = fields.Selection(string="Payslip Tax Type", help="Compute Tax For Employee On Payslip",
                                        selection=[('annual', 'Annually'), ('month', 'Monthly'), ], required=False,
                                        default='month')

    payslip_discount_total = fields.Boolean(string="Payslip Tax Discount Total", )
    payslip_tax_minimum_salary = fields.Integer(string="Payslip Tax Minimum Start", default=9000)
    payslip_tax_minimum_salary_force = fields.Integer(string="Payslip Tax Minimum Force", default=700000)

class HrPayslipConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    payslip_tax_type = fields.Selection(string="Tax Type", help="Compute Tax For Employee On Payslip",
                                        selection=[('annual', 'Annually'), ('month', 'Monthly'), ], required=False,
                                        default='month',related='company_id.payslip_tax_type')
    payslip_tax_minimum_salary = fields.Integer(string="Payslip Tax Minimum Salary",
                                                related='company_id.payslip_tax_minimum_salary', readonly=False)
    payslip_tax_minimum_salary_force = fields.Integer(string="Force Tax Minimum Salary",
                                                      related='company_id.payslip_tax_minimum_salary_force',
                                                      readonly=False)

    def set_payslip_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'res.config.settings', 'payslip_tax_type', self.payslip_tax_type)
