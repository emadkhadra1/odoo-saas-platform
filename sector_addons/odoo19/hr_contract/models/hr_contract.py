from odoo import fields, models


class HrContract(models.Model):
    _name = "hr.contract"
    _description = "Employee Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", tracking=True, ondelete="cascade")
    department_id = fields.Many2one(related="employee_id.department_id", store=True, readonly=True)
    job_id = fields.Many2one(related="employee_id.job_id", store=True, readonly=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="End Date")
    resource_calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    wage = fields.Monetary(string="Wage", currency_field="currency_id")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    state = fields.Selection(
        [
            ("draft", "New"),
            ("open", "Running"),
            ("close", "Expired"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    def action_running(self):
        self.write({"state": "open"})

    def action_close(self):
        self.write({"state": "close"})

    def action_cancel(self):
        self.write({"state": "cancel"})
