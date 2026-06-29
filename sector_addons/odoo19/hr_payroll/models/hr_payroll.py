from odoo import fields, models


class HrPayrollStructureType(models.Model):
    _name = "hr.payroll.structure.type"
    _description = "Payroll Structure Type"

    name = fields.Char(required=True)
    country_id = fields.Many2one("res.country", string="Country")
    wage_type = fields.Selection(
        [("monthly", "Monthly Fixed Wage"), ("hourly", "Hourly Wage")],
        default="monthly",
        required=True,
    )


class HrPayrollStructure(models.Model):
    _name = "hr.payroll.structure"
    _description = "Payroll Structure"

    name = fields.Char(required=True)
    type_id = fields.Many2one("hr.payroll.structure.type", string="Salary Structure Type")
    note = fields.Text()
    input_type_ids = fields.Many2many(
        "hr.payslip.input.type",
        "hr_payslip_input_type_structure_rel",
        "struct_id",
        "input_type_id",
        string="Input Types",
    )


class HrPayslipInputType(models.Model):
    _name = "hr.payslip.input.type"
    _description = "Payslip Input Type"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    struct_ids = fields.Many2many(
        "hr.payroll.structure",
        "hr_payslip_input_type_structure_rel",
        "input_type_id",
        "struct_id",
        string="Available in Structures",
    )


class HrPayslipRun(models.Model):
    _name = "hr.payslip.run"
    _description = "Payslip Batch"
    _order = "date_start desc, id desc"

    name = fields.Char(required=True)
    date_start = fields.Date()
    date_end = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("close", "Done")],
        default="draft",
    )
    slip_ids = fields.One2many("hr.payslip", "payslip_run_id", string="Payslips")


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _description = "Payslip"
    _order = "date_from desc, id desc"

    name = fields.Char(required=True)
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    payslip_run_id = fields.Many2one("hr.payslip.run", string="Batch", ondelete="set null")
    struct_id = fields.Many2one("hr.payroll.structure", string="Salary Structure")
    input_line_ids = fields.One2many("hr.payslip.input", "payslip_id", string="Other Inputs")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancel", "Cancelled")],
        default="draft",
    )


class HrPayslipInput(models.Model):
    _name = "hr.payslip.input"
    _description = "Payslip Input"

    name = fields.Char(required=True)
    payslip_id = fields.Many2one("hr.payslip", required=True, ondelete="cascade")
    input_type_id = fields.Many2one("hr.payslip.input.type", string="Input Type", required=True)
    code = fields.Char(related="input_type_id.code", store=True, readonly=True)
    amount = fields.Float()
