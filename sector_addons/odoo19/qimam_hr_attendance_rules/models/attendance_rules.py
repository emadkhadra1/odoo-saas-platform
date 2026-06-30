from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamAttendancePolicy(models.Model):
    _name = "qimam.attendance.policy"
    _description = "سياسة دوام"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="اسم السياسة", required=True, tracking=True)
    grace_minutes = fields.Integer(string="مهلة التأخير بالدقائق", default=15, tracking=True)
    monthly_permission_minutes = fields.Integer(string="رصيد الاستئذان الشهري بالدقائق", default=120)
    overtime_start_after_minutes = fields.Integer(string="احتساب الإضافي بعد دقائق", default=30)
    line_ids = fields.One2many("qimam.attendance.policy.line", "policy_id", string="بنود القواعد")
    active = fields.Boolean(string="نشطة", default=True)


class QimamAttendancePolicyLine(models.Model):
    _name = "qimam.attendance.policy.line"
    _description = "قاعدة حضور وانصراف"
    _order = "policy_id, sequence, id"

    policy_id = fields.Many2one("qimam.attendance.policy", string="سياسة الدوام", required=True, ondelete="cascade")
    sequence = fields.Integer(string="الترتيب", default=10)
    rule_type = fields.Selection(
        [
            ("late", "تأخير حضور"),
            ("early_checkout", "انصراف مبكر"),
            ("no_checkout", "عدم تسجيل انصراف"),
            ("absence", "غياب"),
            ("overtime", "عمل إضافي"),
        ],
        string="نوع القاعدة",
        required=True,
    )
    from_minutes = fields.Integer(string="من دقيقة", default=0)
    to_minutes = fields.Integer(string="إلى دقيقة", default=0)
    deduction_hours = fields.Float(string="خصم ساعات", default=0.0)
    deduction_days = fields.Float(string="خصم أيام", default=0.0)
    overtime_rate = fields.Float(string="معامل الإضافي", default=1.0)
    notes = fields.Text(string="ملاحظات")

    @api.constrains("from_minutes", "to_minutes")
    def _check_minutes(self):
        for line in self:
            if line.to_minutes and line.to_minutes < line.from_minutes:
                raise ValidationError(_("لا يمكن أن تكون قيمة 'إلى دقيقة' أقل من 'من دقيقة'."))


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    qimam_attendance_policy_id = fields.Many2one("qimam.attendance.policy", string="سياسة الدوام")
