from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QimamHrEndOfService(models.Model):
    _name = "qimam.hr.end.service"
    _description = "تسوية نهاية الخدمة"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "termination_date desc, id desc"

    name = fields.Char(string="رقم التسوية", default="New", copy=False, readonly=True, tracking=True)
    employee_id = fields.Many2one("hr.employee", string="الموظف", required=True, tracking=True, ondelete="restrict")
    contract_id = fields.Many2one(
        "hr.contract",
        string="العقد",
        domain="[('employee_id', '=', employee_id)]",
        tracking=True,
        ondelete="set null",
    )
    department_id = fields.Many2one(string="القسم", related="employee_id.department_id", store=True, readonly=True)
    job_id = fields.Many2one(string="المسمى الوظيفي", related="employee_id.job_id", store=True, readonly=True)
    date_start = fields.Date(string="تاريخ المباشرة", required=True, tracking=True)
    termination_date = fields.Date(string="تاريخ انتهاء العلاقة", required=True, default=fields.Date.context_today, tracking=True)
    termination_type = fields.Selection(
        [
            ("resignation", "استقالة"),
            ("termination", "إنهاء من الشركة"),
            ("contract_end", "انتهاء عقد"),
        ],
        default="contract_end",
        string="سبب نهاية الخدمة",
        required=True,
    )
    wage = fields.Monetary(string="الأجر الأساسي", required=True, currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", string="العملة", default=lambda self: self.env.company.currency_id, required=True)
    service_years = fields.Float(string="مدة الخدمة بالسنوات", compute="_compute_settlement", store=True)
    gratuity_amount = fields.Monetary(string="مكافأة نهاية الخدمة", compute="_compute_settlement", store=True, currency_field="currency_id")
    leave_balance_amount = fields.Monetary(string="رصيد الإجازات", currency_field="currency_id")
    other_allowances = fields.Monetary(string="مستحقات أخرى", currency_field="currency_id")
    deductions = fields.Monetary(string="استقطاعات", currency_field="currency_id")
    net_amount = fields.Monetary(string="صافي المستحق", compute="_compute_settlement", store=True, currency_field="currency_id")
    notes = fields.Text(string="ملاحظات")
    state = fields.Selection(
        [
            ("draft", "مسودة"),
            ("confirmed", "بانتظار الاعتماد"),
            ("approved", "معتمدة"),
            ("paid", "مصروفة"),
            ("cancelled", "ملغاة"),
        ],
        default="draft",
        string="الحالة",
        required=True,
        tracking=True,
    )

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        for settlement in self:
            contract = self.env["hr.contract"].search(
                [("employee_id", "=", settlement.employee_id.id), ("state", "=", "open")],
                limit=1,
            )
            settlement.contract_id = contract
            settlement.date_start = contract.date_start or settlement.date_start
            settlement.wage = contract.wage or settlement.wage

    @api.depends("date_start", "termination_date", "wage", "leave_balance_amount", "other_allowances", "deductions")
    def _compute_settlement(self):
        for settlement in self:
            years = 0.0
            gratuity = 0.0
            if settlement.date_start and settlement.termination_date:
                days = (settlement.termination_date - settlement.date_start).days
                years = max(days / 365.25, 0.0)
                first_period = min(years, 5.0)
                second_period = max(years - 5.0, 0.0)
                gratuity = (first_period * settlement.wage * 0.5) + (second_period * settlement.wage)
            settlement.service_years = years
            settlement.gratuity_amount = gratuity
            settlement.net_amount = gratuity + settlement.leave_balance_amount + settlement.other_allowances - settlement.deductions

    @api.constrains("date_start", "termination_date")
    def _check_dates(self):
        for settlement in self:
            if settlement.date_start and settlement.termination_date and settlement.termination_date < settlement.date_start:
                raise ValidationError(_("لا يمكن أن يكون تاريخ انتهاء العلاقة قبل تاريخ المباشرة."))

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = sequence.next_by_code("qimam.hr.end.service") or "New"
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_mark_paid(self):
        self.write({"state": "paid"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})
