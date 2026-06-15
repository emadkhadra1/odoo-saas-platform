from odoo import api, models
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        self._check_saas_user_limit(extra_users=len([vals for vals in vals_list if vals.get("active", True)]))
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("active") is True:
            inactive_count = len(self.filtered(lambda user: not user.active))
            self._check_saas_user_limit(extra_users=inactive_count)
        return super().write(vals)

    @api.model
    def _check_saas_user_limit(self, extra_users=1):
        limit = int(self.env["ir.config_parameter"].sudo().get_param("saas_manager.allowed_users", "0") or 0)
        if not limit:
            return
        current_users = self.search_count([("active", "=", True), ("share", "=", False)])
        if current_users + extra_users > limit:
            raise UserError("Your subscription allows %s active internal users. Contact support to upgrade your plan." % limit)

    @api.model
    def saas_get_active_users_count(self):
        """Return the active internal user count for master database synchronization."""
        return self.search_count([("active", "=", True), ("share", "=", False)])
