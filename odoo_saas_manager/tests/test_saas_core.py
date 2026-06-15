from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaasCore(TransactionCase):
    def test_tenant_defaults_allowed_users_from_plan(self):
        plan = self.env["saas.plan"].create(
            {
                "name": "Test Plan",
                "code": "TEST",
                "monthly_price": 10,
                "yearly_price": 100,
                "max_users": 7,
            }
        )

        tenant = self.env["saas.tenant"].create(
            {
                "company_name": "Acme",
                "email": "admin@example.com",
                "subdomain": "acme",
                "database_name": "tenant_acme",
                "plan_id": plan.id,
            }
        )

        self.assertEqual(tenant.allowed_users, 7)
        self.assertEqual(tenant.status, "draft")

    def test_invalid_subdomain_is_rejected(self):
        plan = self.env["saas.plan"].create(
            {
                "name": "Validation Plan",
                "code": "VALIDATION",
                "monthly_price": 10,
                "yearly_price": 100,
                "max_users": 1,
            }
        )

        with self.assertRaises(ValidationError):
            self.env["saas.tenant"].create(
                {
                    "company_name": "Bad Tenant",
                    "email": "bad@example.com",
                    "subdomain": "-bad",
                    "database_name": "tenant_bad",
                    "plan_id": plan.id,
                }
            )

    def test_dashboard_metrics_compute(self):
        plan = self.env["saas.plan"].create(
            {
                "name": "Metrics Plan",
                "code": "METRICS",
                "monthly_price": 50,
                "yearly_price": 600,
                "max_users": 3,
            }
        )
        tenant = self.env["saas.tenant"].create(
            {
                "company_name": "Metrics Tenant",
                "email": "metrics@example.com",
                "subdomain": "metrics",
                "database_name": "tenant_metrics",
                "plan_id": plan.id,
                "status": "active",
            }
        )
        self.env["saas.subscription"].create(
            {
                "tenant_id": tenant.id,
                "plan_id": plan.id,
                "billing_cycle": "monthly",
                "subscription_status": "active",
                "payment_status": "paid",
            }
        )

        dashboard = self.env["saas.dashboard"].create({})

        self.assertEqual(dashboard.active_tenants, 1)
        self.assertEqual(dashboard.mrr, 50)
