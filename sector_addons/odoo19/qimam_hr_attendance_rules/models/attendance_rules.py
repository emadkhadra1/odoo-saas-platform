from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamAttendancePolicy(models.Model):
    _name = "qimam.attendance.policy"
    _description = "Attendance Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    grace_minutes = fields.Integer(default=15, tracking=True)
    monthly_permission_minutes = fields.Integer(default=120)
    overtime_start_after_minutes = fields.Integer(default=30)
    line_ids = fields.One2many("qimam.attendance.policy.line", "policy_id", string="Rules")
    active = fields.Boolean(default=True)


class QimamAttendancePolicyLine(models.Model):
    _name = "qimam.attendance.policy.line"
    _description = "Attendance Policy Rule"
    _order = "policy_id, sequence, id"

    policy_id = fields.Many2one("qimam.attendance.policy", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    rule_type = fields.Selection(
        [
            ("late", "Late Check In"),
            ("early_checkout", "Early Check Out"),
            ("no_checkout", "Missing Check Out"),
            ("absence", "Absence"),
            ("overtime", "Overtime"),
        ],
        required=True,
    )
    from_minutes = fields.Integer(default=0)
    to_minutes = fields.Integer(default=0)
    deduction_hours = fields.Float(default=0.0)
    deduction_days = fields.Float(default=0.0)
    overtime_rate = fields.Float(default=1.0)
    notes = fields.Text()

    @api.constrains("from_minutes", "to_minutes")
    def _check_minutes(self):
        for line in self:
            if line.to_minutes and line.to_minutes < line.from_minutes:
                raise ValidationError(_("To minutes cannot be less than from minutes."))


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    qimam_attendance_policy_id = fields.Many2one("qimam.attendance.policy", string="Attendance Policy")
