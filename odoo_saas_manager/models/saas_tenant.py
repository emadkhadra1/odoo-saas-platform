import re
import uuid

from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.modules.registry import Registry

from ..services.provisioning_service import TenantProvisioningService


SUBDOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
DB_NAME_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62}$")


class SaasTenant(models.Model):
    """Master database representation of an isolated tenant database."""

    _name = "saas.tenant"
    _description = "SaaS Tenant"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(required=True, default=lambda self: self.env["ir.sequence"].next_by_code("saas.tenant") or "New")
    company_name = fields.Char(required=True, tracking=True)
    contact_name = fields.Char(tracking=True)
    email = fields.Char(required=True, tracking=True)
    phone = fields.Char(tracking=True)
    subdomain = fields.Char(required=True, tracking=True)
    database_name = fields.Char(required=True, tracking=True)
    database_uuid = fields.Char(default=lambda self: str(uuid.uuid4()), readonly=True, copy=False)
    plan_id = fields.Many2one("saas.plan", required=True, tracking=True)
    subscription_id = fields.Many2one("saas.subscription", tracking=True)
    allowed_users = fields.Integer(default=1, tracking=True)
    active_users_count = fields.Integer(readonly=True, tracking=True)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("provisioning", "Provisioning"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    start_date = fields.Date(tracking=True)
    expiry_date = fields.Date(tracking=True)
    last_payment_date = fields.Date(tracking=True)
    next_invoice_date = fields.Date(tracking=True)
    notes = fields.Text()
    provisioning_log_ids = fields.One2many("saas.provisioning.log", "tenant_id")
    payment_ids = fields.One2many("saas.payment", "tenant_id")
    subscription_ids = fields.One2many("saas.subscription", "tenant_id")

    _sql_constraints = [
        ("saas_tenant_subdomain_unique", "unique(subdomain)", "The tenant subdomain must be unique."),
        ("saas_tenant_database_unique", "unique(database_name)", "The tenant database name must be unique."),
        ("saas_tenant_database_uuid_unique", "unique(database_uuid)", "The tenant database UUID must be unique."),
        ("saas_tenant_allowed_users_positive", "check(allowed_users >= 0)", "Allowed users cannot be negative."),
        ("saas_tenant_active_users_positive", "check(active_users_count >= 0)", "Active users cannot be negative."),
    ]

    @api.onchange("plan_id")
    def _onchange_plan_id(self):
        for tenant in self:
            if tenant.plan_id:
                tenant.allowed_users = tenant.plan_id.max_users

    @api.constrains("subdomain")
    def _check_subdomain(self):
        for tenant in self:
            value = (tenant.subdomain or "").strip().lower()
            if value and not SUBDOMAIN_RE.match(value):
                raise ValidationError("Subdomain must be a valid DNS label, for example client1.")

    @api.constrains("database_name")
    def _check_database_name(self):
        for tenant in self:
            value = (tenant.database_name or "").strip()
            if value and not DB_NAME_RE.match(value):
                raise ValidationError("Database name may only contain letters, numbers, underscores, and hyphens.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("subdomain"):
                vals["subdomain"] = vals["subdomain"].strip().lower()
            if vals.get("plan_id") and not vals.get("allowed_users"):
                vals["allowed_users"] = self.env["saas.plan"].browse(vals["plan_id"]).max_users
        return super().create(vals_list)

    def action_mark_provisioning(self):
        for tenant in self:
            TenantProvisioningService(self.env).provision(tenant)
        return True

    def action_activate(self):
        self.write({"status": "active"})

    def action_suspend(self):
        for tenant in self:
            TenantProvisioningService(self.env).suspend_database(tenant)
        return True

    def action_reactivate(self):
        for tenant in self:
            TenantProvisioningService(self.env).reactivate_database(tenant)
        return True

    def action_cancel(self):
        self.write({"status": "cancelled"})

    def action_open_tenant_database(self):
        self.ensure_one()
        if not self.database_name:
            raise ValidationError("Set the tenant database name before opening the tenant.")
        return {
            "type": "ir.actions.act_url",
            "url": "/web?db=%s" % self.database_name,
            "target": "self",
        }

    def _get_or_create_billing_partner(self):
        self.ensure_one()
        partner = self.env["res.partner"].search([("email", "=", self.email)], limit=1)
        if partner:
            return partner
        return self.env["res.partner"].create(
            {
                "name": self.company_name,
                "email": self.email,
                "phone": self.phone,
                "company_type": "company",
            }
        )

    def sync_active_users_count(self):
        """Refresh the active internal user count from the isolated tenant database."""
        for tenant in self:
            with Registry(tenant.database_name).cursor() as cursor:
                env = api.Environment(cursor, SUPERUSER_ID, {})
                count = env["res.users"].saas_get_active_users_count()
                tenant.active_users_count = count
        return True
