from odoo import api, fields, models


class RetirementPercentage(models.Model):
    _name = 'retirement.percentage'
    _rec_name = 'employee_percentage'

    employee_percentage = fields.Float(string="Employee %")
    school_percentage = fields.Float(string="Company %")
