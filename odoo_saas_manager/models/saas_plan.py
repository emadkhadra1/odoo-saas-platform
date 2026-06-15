from odoo import api, fields, models


class SaasPlan(models.Model):
    """Commercial package that controls tenant limits and enabled Odoo apps."""

    _name = "saas.plan"
    _description = "SaaS Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "monthly_price, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    monthly_price = fields.Monetary(required=True, default=0.0, tracking=True)
    yearly_price = fields.Monetary(required=True, default=0.0, tracking=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    max_users = fields.Integer(required=True, default=1, tracking=True)
    included_modules = fields.Text(
        help="Technical module names included by this plan, one per line or comma-separated."
    )
    allowed_apps = fields.Many2many(
        "ir.module.module",
        "saas_plan_ir_module_rel",
        "plan_id",
        "module_id",
        string="Allowed Apps",
        domain=[("application", "=", True)],
    )
    storage_limit = fields.Float(help="Storage limit in GB.")
    trial_days = fields.Integer(default=0)
    is_active = fields.Boolean(default=True, tracking=True)
    description = fields.Text()

    _sql_constraints = [
        ("saas_plan_code_unique", "unique(code)", "The plan code must be unique."),
        ("saas_plan_max_users_positive", "check(max_users >= 0)", "Maximum users cannot be negative."),
        ("saas_plan_prices_positive", "check(monthly_price >= 0 and yearly_price >= 0)", "Plan prices cannot be negative."),
    ]

    @api.depends("name", "code")
    def _compute_display_name(self):
        for plan in self:
            plan.display_name = f"{plan.name} [{plan.code}]" if plan.code else plan.name
