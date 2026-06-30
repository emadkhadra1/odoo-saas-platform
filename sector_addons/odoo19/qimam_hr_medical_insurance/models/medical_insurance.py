from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamHrMedicalPolicy(models.Model):
    _name = "qimam.hr.medical.policy"
    _description = "وثيقة تأمين طبي"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(string="اسم الوثيقة", required=True, tracking=True)
    provider = fields.Char(string="شركة التأمين", required=True, tracking=True)
    policy_number = fields.Char(string="رقم الوثيقة", required=True, tracking=True)
    date_start = fields.Date(string="تاريخ البداية", required=True)
    date_end = fields.Date(string="تاريخ النهاية", required=True)
    currency_id = fields.Many2one("res.currency", string="العملة", default=lambda self: self.env.company.currency_id, required=True)
    annual_premium = fields.Monetary(string="القسط السنوي", currency_field="currency_id")
    member_ids = fields.One2many("qimam.hr.medical.member", "policy_id", string="الموظفون المؤمن عليهم")
    member_count = fields.Integer(string="عدد المؤمن عليهم", compute="_compute_member_count")
    state = fields.Selection(
        [("draft", "مسودة"), ("active", "نشطة"), ("expired", "منتهية"), ("cancelled", "ملغاة")],
        string="الحالة",
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
                raise ValidationError(_("لا يمكن أن يكون تاريخ نهاية الوثيقة قبل تاريخ البداية."))

    def action_activate(self):
        self.write({"state": "active"})

    def action_expire(self):
        self.write({"state": "expired"})

    def action_cancel(self):
        self.write({"state": "cancelled"})


class QimamHrMedicalMember(models.Model):
    _name = "qimam.hr.medical.member"
    _description = "تأمين طبي للموظف"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", string="الموظف", required=True, tracking=True, ondelete="cascade")
    policy_id = fields.Many2one("qimam.hr.medical.policy", string="وثيقة التأمين", required=True, tracking=True, ondelete="restrict")
    provider = fields.Char(string="شركة التأمين", related="policy_id.provider", store=True, readonly=True)
    policy_number = fields.Char(string="رقم الوثيقة", related="policy_id.policy_number", store=True, readonly=True)
    insurance_class = fields.Selection(
        [("vip", "VIP"), ("a", "فئة A"), ("b", "فئة B"), ("c", "فئة C")],
        string="فئة التأمين",
        default="b",
        required=True,
        tracking=True,
    )
    membership_number = fields.Char(string="رقم العضوية", tracking=True)
    date_start = fields.Date(string="تاريخ البداية", related="policy_id.date_start", store=True, readonly=True)
    date_end = fields.Date(string="تاريخ النهاية", related="policy_id.date_end", store=True, readonly=True)
    dependent_count = fields.Integer(string="عدد التابعين", default=0)
    premium_amount = fields.Monetary(string="قسط الموظف", currency_field="currency_id")
    currency_id = fields.Many2one(string="العملة", related="policy_id.currency_id", readonly=True)
    state = fields.Selection(
        [("active", "نشط"), ("suspended", "موقوف"), ("expired", "منتهي")],
        string="الحالة",
        default="active",
        tracking=True,
    )
    notes = fields.Text(string="ملاحظات")

    def action_suspend(self):
        self.write({"state": "suspended"})

    def action_activate(self):
        self.write({"state": "active"})

    def action_expire(self):
        self.write({"state": "expired"})


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    medical_insurance_count = fields.Integer(string="عدد وثائق التأمين", compute="_compute_medical_insurance_count")

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
            "name": _("التأمين الطبي"),
            "res_model": "qimam.hr.medical.member",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
