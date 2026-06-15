import base64
import csv
import io
import logging

from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)


DATASET_RULES = {
    "employees": {"model": "hr.employee", "required": ["name"], "fields": ["name", "work_email", "work_phone"]},
    "properties": {"model": "estate.property", "required": ["name"], "fields": ["name", "description"]},
    "projects": {"model": "project.project", "required": ["name"], "fields": ["name"]},
    "students": {"model": "school.student", "required": ["name"], "fields": ["name", "email", "phone"]},
    "customers": {"model": "res.partner", "required": ["name"], "fields": ["name", "email", "phone"]},
}


class SaasOnboardingImportWizard(models.TransientModel):
    _name = "saas.onboarding.import.wizard"
    _description = "SaaS Onboarding Import Wizard"

    tenant_id = fields.Many2one("saas.tenant", required=True, domain=[("status", "in", ("active", "provisioning"))])
    data_type = fields.Selection(
        [
            ("employees", "Employees"),
            ("properties", "Properties"),
            ("projects", "Projects"),
            ("students", "Students"),
            ("customers", "Customers"),
        ],
        required=True,
    )
    upload_file = fields.Binary(required=True)
    filename = fields.Char(required=True)
    result = fields.Text(readonly=True)

    def action_import(self):
        self.ensure_one()
        rows = self._read_rows()
        rule = DATASET_RULES[self.data_type]
        self._validate_columns(rows, rule)
        imported = self._import_into_tenant(rows, rule)
        self.result = "Imported %s %s rows into %s." % (imported, self.data_type, self.tenant_id.database_name)
        self.env["saas.provisioning.log"].sudo().create(
            {
                "tenant_id": self.tenant_id.id,
                "action": "onboarding_import",
                "status": "success",
                "message": self.result,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _read_rows(self):
        content = base64.b64decode(self.upload_file)
        filename = (self.filename or "").lower()
        if filename.endswith(".csv"):
            text = content.decode("utf-8-sig")
            return list(csv.DictReader(io.StringIO(text)))
        if filename.endswith(".xlsx"):
            try:
                import openpyxl
            except ImportError as exc:
                raise UserError("Install openpyxl on the Odoo server to import XLSX files.") from exc
            workbook = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            sheet = workbook.active
            headers = [str(cell.value).strip() if cell.value is not None else "" for cell in next(sheet.rows)]
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                rows.append({headers[index]: value for index, value in enumerate(row) if index < len(headers)})
            return rows
        raise UserError("Only CSV and XLSX files are supported.")

    def _validate_columns(self, rows, rule):
        if not rows:
            raise UserError("The uploaded file is empty.")
        headers = set(rows[0].keys())
        missing = [column for column in rule["required"] if column not in headers]
        if missing:
            raise UserError("Missing required columns: %s" % ", ".join(missing))

    def _import_into_tenant(self, rows, rule):
        imported = 0
        with Registry(self.tenant_id.database_name).cursor() as cursor:
            env = api.Environment(cursor, SUPERUSER_ID, {})
            if rule["model"] not in env:
                raise UserError("Model %s is not installed in tenant database." % rule["model"])
            Model = env[rule["model"]]
            allowed_fields = set(Model._fields)
            for row in rows:
                vals = {
                    field: row.get(field)
                    for field in rule["fields"]
                    if field in allowed_fields and row.get(field) not in (None, "")
                }
                if vals:
                    Model.create(vals)
                    imported += 1
            cursor.commit()
        _logger.info("Imported %s rows into %s for tenant %s", imported, rule["model"], self.tenant_id.database_name)
        return imported
