from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamHrDocumentType(models.Model):
    _name = "qimam.hr.document.type"
    _description = "Employee Document Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    requires_expiry = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Document type code must be unique."),
    ]


class QimamHrDocument(models.Model):
    _name = "qimam.hr.document"
    _description = "Employee Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date, id desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    employee_id = fields.Many2one("hr.employee", required=True, tracking=True, ondelete="cascade")
    document_type_id = fields.Many2one("qimam.hr.document.type", required=True, tracking=True)
    document_number = fields.Char(tracking=True)
    issue_place = fields.Char()
    issue_date = fields.Date(tracking=True)
    expiry_date = fields.Date(tracking=True)
    days_to_expire = fields.Integer(compute="_compute_expiry", store=True)
    expiry_status = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring", "Expiring Soon"),
            ("expired", "Expired"),
            ("no_expiry", "No Expiry"),
        ],
        compute="_compute_expiry",
        store=True,
    )
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    notes = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    @api.depends("employee_id", "document_type_id", "document_number")
    def _compute_name(self):
        for document in self:
            parts = [document.employee_id.name or "", document.document_type_id.name or ""]
            if document.document_number:
                parts.append(document.document_number)
            document.name = " - ".join([part for part in parts if part]) or _("Employee Document")

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
                raise ValidationError(_("Expiry date cannot be before issue date."))

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

    qimam_document_count = fields.Integer(compute="_compute_qimam_document_count")

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
            "name": _("Employee Documents"),
            "res_model": "qimam.hr.document",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
