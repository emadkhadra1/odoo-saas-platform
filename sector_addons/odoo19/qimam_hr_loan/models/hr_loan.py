from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QimamHrLoan(models.Model):
    _name = "qimam.hr.loan"
    _description = "السلف والقروض للموظفين"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, id desc"

    name = fields.Char(string="رقم الطلب", default="New", copy=False, readonly=True, tracking=True)
    employee_id = fields.Many2one("hr.employee", string="الموظف", required=True, tracking=True, ondelete="restrict")
    department_id = fields.Many2one(string="القسم", related="employee_id.department_id", store=True, readonly=True)
    job_id = fields.Many2one(string="المسمى الوظيفي", related="employee_id.job_id", store=True, readonly=True)
    request_date = fields.Date(string="تاريخ الطلب", default=fields.Date.context_today, required=True, tracking=True)
    loan_type = fields.Selection(
        [("loan", "قرض موظف"), ("advance", "سلفة راتب")],
        string="نوع الطلب",
        default="advance",
        required=True,
        tracking=True,
    )
    reason = fields.Text(string="سبب الطلب", required=True)
    amount = fields.Monetary(string="المبلغ", required=True, tracking=True, currency_field="currency_id")
    installment_count = fields.Integer(string="عدد الأقساط", default=1, required=True)
    first_deduction_date = fields.Date(string="تاريخ أول استقطاع", default=fields.Date.context_today, required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="العملة",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    line_ids = fields.One2many("qimam.hr.loan.line", "loan_id", string="الأقساط", copy=False)
    paid_amount = fields.Monetary(string="المبلغ المسدد", compute="_compute_amounts", currency_field="currency_id", store=True)
    balance_amount = fields.Monetary(string="الرصيد المتبقي", compute="_compute_amounts", currency_field="currency_id", store=True)
    state = fields.Selection(
        [
            ("draft", "مسودة"),
            ("submitted", "بانتظار الاعتماد"),
            ("approved", "معتمدة"),
            ("running", "تحت الاستقطاع"),
            ("paid", "مسددة"),
            ("refused", "مرفوضة"),
            ("cancelled", "ملغاة"),
        ],
        default="draft",
        string="الحالة",
        required=True,
        tracking=True,
    )

    @api.depends("amount", "line_ids.amount", "line_ids.paid")
    def _compute_amounts(self):
        for loan in self:
            loan.paid_amount = sum(loan.line_ids.filtered("paid").mapped("amount"))
            loan.balance_amount = loan.amount - loan.paid_amount

    @api.constrains("amount", "installment_count")
    def _check_positive_amounts(self):
        for loan in self:
            if loan.amount <= 0:
                raise ValidationError(_("يجب أن يكون مبلغ السلفة أو القرض أكبر من صفر."))
            if loan.installment_count <= 0:
                raise ValidationError(_("يجب أن يكون عدد الأقساط أكبر من صفر."))

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = sequence.next_by_code("qimam.hr.loan") or "New"
        return super().create(vals_list)

    def action_compute_installments(self):
        for loan in self:
            if loan.state not in ("draft", "submitted"):
                raise UserError(_("لا يمكن إعادة احتساب الأقساط إلا قبل الاعتماد."))
            loan.line_ids.unlink()
            installment_amount = loan.amount / loan.installment_count
            current_date = loan.first_deduction_date
            for index in range(loan.installment_count):
                self.env["qimam.hr.loan.line"].create(
                    {
                        "loan_id": loan.id,
                        "employee_id": loan.employee_id.id,
                        "date": current_date,
                        "amount": installment_amount,
                        "sequence": index + 1,
                    }
                )
                current_date += relativedelta(months=1)

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        for loan in self:
            if not loan.line_ids:
                loan.action_compute_installments()
            loan.state = "approved"

    def action_start_deduction(self):
        self.write({"state": "running"})

    def action_mark_paid(self):
        for loan in self:
            loan.line_ids.write({"paid": True})
            loan.state = "paid"

    def action_refuse(self):
        self.write({"state": "refused"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})


class QimamHrLoanLine(models.Model):
    _name = "qimam.hr.loan.line"
    _description = "قسط سلفة أو قرض موظف"
    _order = "date, sequence, id"

    loan_id = fields.Many2one("qimam.hr.loan", string="طلب السلفة أو القرض", required=True, ondelete="cascade")
    sequence = fields.Integer(string="م", default=1)
    employee_id = fields.Many2one("hr.employee", string="الموظف", required=True, ondelete="restrict")
    date = fields.Date(string="تاريخ القسط", required=True)
    amount = fields.Monetary(string="مبلغ القسط", required=True, currency_field="currency_id")
    currency_id = fields.Many2one(string="العملة", related="loan_id.currency_id", readonly=True)
    paid = fields.Boolean(string="مسدد")
    payslip_id = fields.Many2one("hr.payslip", string="مسير الراتب")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_count = fields.Integer(string="عدد السلف والقروض", compute="_compute_qimam_loan_count")

    def _compute_qimam_loan_count(self):
        grouped = self.env["qimam.hr.loan"].read_group(
            [("employee_id", "in", self.ids)],
            ["employee_id"],
            ["employee_id"],
        )
        counts = {item["employee_id"][0]: item.get("employee_id_count", item.get("__count", 0)) for item in grouped}
        for employee in self:
            employee.loan_count = counts.get(employee.id, 0)

    def action_open_qimam_loans(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("السلف والقروض"),
            "res_model": "qimam.hr.loan",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
