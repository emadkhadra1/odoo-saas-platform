from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamHrMedicalPolicy(models.Model):
    _name = "qimam.hr.medical.policy"
    _description = "Medical Insurance Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    provider = fields.Char(required=True, tracking=True)
    policy_number = fields.Char(required=True, tracking=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, required=True)
    annual_premium = fields.Monetary(currency_field="currency_id")
    member_ids = fields.One2many("qimam.hr.medical.member", "policy_id", string="Covered Employees")
    member_count = fields.Integer(compute="_compute_member_count")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired"), ("cancelled", "Cancelled")],
        default="draft",
        tracking=True,
    )

    @api.depends("member_ids")
    def _compute_member_count(self):
        for policy in self:
            policy.member_count = len(policy.member_ids)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for policy in self:
            if policy.date_start and policy.date_end and policy.date_end < policy.date_start:
                raise ValidationError(_("Policy end date cannot be before start date."))

    def action_activate(self):
        self.write({"state": "active"})

    def action_expire(self):
        self.write({"state": "expired"})

    def action_cancel(self):
        self.write({"state": "cancelled"})


class QimamHrMedicalMember(models.Model):
    _name = "qimam.hr.medical.member"
    _description = "Employee Medical Insurance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", required=True, tracking=True, ondelete="cascade")
    policy_id = fields.Many2one("qimam.hr.medical.policy", required=True, tracking=True, ondelete="restrict")
    provider = fields.Char(related="policy_id.provider", store=True, readonly=True)
    policy_number = fields.Char(related="policy_id.policy_number", store=True, readonly=True)
    insurance_class = fields.Selection(
        [("vip", "VIP"), ("a", "Class A"), ("b", "Class B"), ("c", "Class C")],
        default="b",
        required=True,
        tracking=True,
    )
    membership_number = fields.Char(tracking=True)
    date_start = fields.Date(related="policy_id.date_start", store=True, readonly=True)
    date_end = fields.Date(related="policy_id.date_end", store=True, readonly=True)
    dependent_count = fields.Integer(default=0)
    premium_amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(related="policy_id.currency_id", readonly=True)
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended"), ("expired", "Expired")],
        default="active",
        tracking=True,
    )
    notes = fields.Text()

    def action_suspend(self):
        self.write({"state": "suspended"})

    def action_activate(self):
        self.write({"state": "active"})

    def action_expire(self):
        self.write({"state": "expired"})


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    medical_insurance_count = fields.Integer(compute="_compute_medical_insurance_count")

    def _compute_medical_insurance_count(self):
        grouped = self.env["qimam.hr.medical.member"].read_group(
            [("employee_id", "in", self.ids)],
            ["employee_id"],
            ["employee_id"],
        )
        counts = {item["employee_id"][0]: item.get("employee_id_count", item.get("__count", 0)) for item in grouped}
        for employee in self:
            employee.medical_insurance_count = counts.get(employee.id, 0)

    def action_open_medical_insurance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Medical Insurance"),
            "res_model": "qimam.hr.medical.member",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
