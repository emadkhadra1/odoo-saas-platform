from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustodyProperty(models.Model):
    _name = "custody.property"
    _description = "Custody Property"
    _order = "name"

    name = fields.Char(required=True)
    product_id = fields.Many2one("product.product", string="Related Product")
    description = fields.Text()
    active = fields.Boolean(default=True)


class HrCustody(models.Model):
    _name = "hr.custody"
    _description = "Employee Custody"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_request desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    custody_name = fields.Many2one("custody.property", string="Custody", required=True, tracking=True)
    employee = fields.Many2one("hr.employee", required=True, tracking=True)
    department_id = fields.Many2one(related="employee.department_id", store=True, readonly=True)
    job_id = fields.Many2one(related="employee.job_id", store=True, readonly=True)
    purpose = fields.Text(required=True)
    date_request = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    return_date = fields.Date(tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("returned", "Returned"),
            ("refused", "Refused"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        required=True,
    )

    @api.constrains("date_request", "return_date")
    def _check_return_date(self):
        for rec in self:
            if rec.return_date and rec.date_request and rec.return_date < rec.date_request:
                raise ValidationError(_("Return date cannot be before request date."))

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = sequence.next_by_code("hr.custody") or "New"
        return super().create(vals_list)

    def action_request(self):
        self.write({"state": "requested"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_return(self):
        self.write({"state": "returned", "return_date": fields.Date.context_today(self)})

    def action_refuse(self):
        self.write({"state": "refused"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    custody_count = fields.Integer(compute="_compute_custody_count")

    def _compute_custody_count(self):
        counts = self.env["hr.custody"].read_group(
            [("employee", "in", self.ids)],
            ["employee"],
            ["employee"],
        )
        mapped = {item["employee"][0]: item.get("employee_count", item.get("__count", 0)) for item in counts}
        for employee in self:
            employee.custody_count = mapped.get(employee.id, 0)

    def action_open_custodies(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Custodies"),
            "res_model": "hr.custody",
            "view_mode": "list,form",
            "domain": [("employee", "=", self.id)],
            "context": {"default_employee": self.id},
        }
