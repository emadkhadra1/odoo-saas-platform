from odoo import api, fields, models


class SaasDashboard(models.TransientModel):
    _name = "saas.dashboard"
    _description = "SaaS Dashboard"

    active_tenants = fields.Integer(compute="_compute_metrics")
    expired_subscriptions = fields.Integer(compute="_compute_metrics")
    mrr = fields.Monetary(compute="_compute_metrics", currency_field="currency_id")
    arr = fields.Monetary(compute="_compute_metrics", currency_field="currency_id")
    suspended_tenants = fields.Integer(compute="_compute_metrics")
    trial_tenants = fields.Integer(compute="_compute_metrics")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends_context("uid")
    def _compute_metrics(self):
        Tenant = self.env["saas.tenant"]
        Subscription = self.env["saas.subscription"]
        active_subscriptions = Subscription.search([("subscription_status", "=", "active")])
        trial_tenant_ids = Subscription.search([("subscription_status", "=", "trial")]).mapped("tenant_id").ids
        monthly_total = sum(
            subscription.amount if subscription.billing_cycle == "monthly" else subscription.amount / 12.0
            for subscription in active_subscriptions
        )
        for dashboard in self:
            dashboard.active_tenants = Tenant.search_count([("status", "=", "active")])
            dashboard.expired_subscriptions = Subscription.search_count([("subscription_status", "=", "expired")])
            dashboard.mrr = monthly_total
            dashboard.arr = monthly_total * 12.0
            dashboard.suspended_tenants = Tenant.search_count([("status", "=", "suspended")])
            dashboard.trial_tenants = Tenant.search_count([("id", "in", trial_tenant_ids)])

    @api.model
    def action_open_dashboard(self):
        dashboard = self.create({})
        return {
            "type": "ir.actions.act_window",
            "name": "SaaS Dashboard",
            "res_model": "saas.dashboard",
            "res_id": dashboard.id,
            "view_mode": "form",
            "target": "current",
        }
