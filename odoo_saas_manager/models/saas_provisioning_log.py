from odoo import fields, models


class SaasProvisioningLog(models.Model):
    """Append-only operational history for tenant provisioning steps."""

    _name = "saas.provisioning.log"
    _description = "SaaS Provisioning Log"
    _order = "create_date desc"

    tenant_id = fields.Many2one("saas.tenant", required=True, ondelete="cascade", index=True)
    action = fields.Char(required=True)
    status = fields.Selection(
        [("pending", "Pending"), ("success", "Success"), ("failed", "Failed"), ("warning", "Warning")],
        default="pending",
        required=True,
    )
    message = fields.Char()
    technical_details = fields.Text()
