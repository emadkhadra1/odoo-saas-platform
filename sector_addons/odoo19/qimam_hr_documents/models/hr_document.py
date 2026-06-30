from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamHrDocumentType(models.Model):
    _name = "qimam.hr.document.type"
    _description = "نوع وثيقة الموظف"
    _order = "sequence, name"

    name = fields.Char(string="نوع الوثيقة", required=True, translate=True)
    code = fields.Char(string="الكود", required=True)
    sequence = fields.Integer(string="الترتيب", default=10)
    active = fields.Boolean(string="نشط", default=True)
    requires_expiry = fields.Boolean(string="لها تاريخ انتهاء", default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "يجب أن يكون كود نوع الوثيقة غير مكرر."),
    ]


class QimamHrDocument(models.Model):
    _name = "qimam.hr.document"
    _description = "وثيقة موظف"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date, id desc"
    _rec_name = "name"

    name = fields.Char(string="اسم الوثيقة", compute="_compute_name", store=True)
    employee_id = fields.Many2one("hr.employee", string="الموظف", required=True, tracking=True, ondelete="cascade")
    document_type_id = fields.Many2one("qimam.hr.document.type", string="نوع الوثيقة", required=True, tracking=True)
    document_number = fields.Char(string="رقم الوثيقة", tracking=True)
    issue_place = fields.Char(string="مكان الإصدار")
    issue_date = fields.Date(string="تاريخ الإصدار", tracking=True)
    expiry_date = fields.Date(string="تاريخ الانتهاء", tracking=True)
    days_to_expire = fields.Integer(string="الأيام المتبقية", compute="_compute_expiry", store=True)
    expiry_status = fields.Selection(
        [
            ("valid", "سارية"),
            ("expiring", "قريبة الانتهاء"),
            ("expired", "منتهية"),
            ("no_expiry", "بدون انتهاء"),
        ],
        string="حالة الانتهاء",
        compute="_compute_expiry",
        store=True,
    )
    attachment_ids = fields.Many2many("ir.attachment", string="المرفقات")
    notes = fields.Text(string="ملاحظات")
    state = fields.Selection(
        [
            ("draft", "مسودة"),
            ("confirmed", "مؤكدة"),
            ("expired", "منتهية"),
            ("cancelled", "ملغاة"),
        ],
        string="الحالة",
        default="draft",
        tracking=True,
    )

    @api.depends("employee_id", "document_type_id", "document_number")
    def _compute_name(self):
        for document in self:
            parts = [document.employee_id.name or "", document.document_type_id.name or ""]
            if document.document_number:
                parts.append(document.document_number)
            document.name = " - ".join([part for part in parts if part]) or _("وثيقة موظف")

    @api.depends("expiry_date", "document_type_id.requires_expiry")
    def _compute_expiry(self):
        today = fields.Date.context_today(self)
        for document in self:
            if not document.document_type_id.requires_expiry or not document.expiry_date:
                document.days_to_expire = 0
                document.expiry_status = "no_expiry"
                continue
            days = (document.expiry_date - today).days
            document.days_to_expire = days
            if days < 0:
                document.expiry_status = "expired"
            elif days <= 30:
                document.expiry_status = "expiring"
            else:
                document.expiry_status = "valid"

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for document in self:
            if document.issue_date and document.expiry_date and document.expiry_date < document.issue_date:
                raise ValidationError(_("لا يمكن أن يكون تاريخ الانتهاء قبل تاريخ الإصدار."))

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_mark_expired(self):
        self.write({"state": "expired"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    qimam_document_count = fields.Integer(string="عدد الوثائق", compute="_compute_qimam_document_count")

    def _compute_qimam_document_count(self):
        grouped = self.env["qimam.hr.document"].read_group(
            [("employee_id", "in", self.ids)],
            ["employee_id"],
            ["employee_id"],
        )
        counts = {item["employee_id"][0]: item.get("employee_id_count", item.get("__count", 0)) for item in grouped}
        for employee in self:
            employee.qimam_document_count = counts.get(employee.id, 0)

    def action_open_qimam_documents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("وثائق الموظفين"),
            "res_model": "qimam.hr.document",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
