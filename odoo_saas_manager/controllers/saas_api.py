from odoo import http
from odoo.http import request


class SaasApiController(http.Controller):
    def _check_api_key(self, token):
        configured = request.env["ir.config_parameter"].sudo().get_param("saas_manager.api_key")
        return configured and token and configured == token

    def _unauthorized(self):
        return {"ok": False, "error": "unauthorized"}

    def _tenant_payload(self, tenant):
        return {
            "id": tenant.id,
            "name": tenant.name,
            "company_name": tenant.company_name,
            "subdomain": tenant.subdomain,
            "database_name": tenant.database_name,
            "database_uuid": tenant.database_uuid,
            "status": tenant.status,
            "allowed_users": tenant.allowed_users,
            "active_users_count": tenant.active_users_count,
        }

    @http.route("/saas/api/tenant/create", type="json", auth="none", csrf=False, methods=["POST"])
    def create_tenant(self, token=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        tenant = request.env["saas.tenant"].sudo().create(
            {
                "company_name": payload.get("company_name"),
                "contact_name": payload.get("contact_name"),
                "email": payload.get("email"),
                "phone": payload.get("phone"),
                "subdomain": payload.get("subdomain"),
                "database_name": payload.get("database_name"),
                "plan_id": payload.get("plan_id"),
                "start_date": payload.get("start_date"),
                "expiry_date": payload.get("expiry_date"),
                "notes": payload.get("notes"),
            }
        )
        if payload.get("provision"):
            tenant.action_mark_provisioning()
        return {"ok": True, "tenant": self._tenant_payload(tenant)}

    @http.route("/saas/api/tenant/status", type="json", auth="none", csrf=False, methods=["POST"])
    def tenant_status(self, token=None, tenant_id=None, subdomain=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        tenant = self._find_tenant(tenant_id, subdomain)
        return {"ok": bool(tenant), "tenant": self._tenant_payload(tenant) if tenant else False}

    @http.route("/saas/api/tenant/suspend", type="json", auth="none", csrf=False, methods=["POST"])
    def suspend_tenant(self, token=None, tenant_id=None, subdomain=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        tenant = self._find_tenant(tenant_id, subdomain)
        if not tenant:
            return {"ok": False, "error": "tenant_not_found"}
        tenant.action_suspend()
        return {"ok": True, "tenant": self._tenant_payload(tenant)}

    @http.route("/saas/api/tenant/reactivate", type="json", auth="none", csrf=False, methods=["POST"])
    def reactivate_tenant(self, token=None, tenant_id=None, subdomain=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        tenant = self._find_tenant(tenant_id, subdomain)
        if not tenant:
            return {"ok": False, "error": "tenant_not_found"}
        tenant.action_reactivate()
        return {"ok": True, "tenant": self._tenant_payload(tenant)}

    @http.route("/saas/api/tenant/change-plan", type="json", auth="none", csrf=False, methods=["POST"])
    def change_plan(self, token=None, tenant_id=None, subdomain=None, plan_id=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        tenant = self._find_tenant(tenant_id, subdomain)
        if not tenant:
            return {"ok": False, "error": "tenant_not_found"}
        plan = request.env["saas.plan"].sudo().browse(plan_id)
        if not plan.exists():
            return {"ok": False, "error": "plan_not_found"}
        tenant.write({"plan_id": plan.id, "allowed_users": plan.max_users})
        if tenant.subscription_id:
            tenant.subscription_id.write({"plan_id": plan.id})
        return {"ok": True, "tenant": self._tenant_payload(tenant)}

    @http.route("/saas/api/payment/record", type="json", auth="none", csrf=False, methods=["POST"])
    def record_payment(self, token=None, tenant_id=None, subscription_id=None, amount=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        payment = request.env["saas.payment"].sudo().create(
            {
                "tenant_id": tenant_id,
                "subscription_id": subscription_id,
                "amount": amount,
                "currency_id": payload.get("currency_id") or request.env.company.currency_id.id,
                "payment_date": payload.get("payment_date"),
                "payment_method": payload.get("payment_method"),
                "transaction_reference": payload.get("transaction_reference"),
                "status": payload.get("status") or "paid",
                "notes": payload.get("notes"),
            }
        )
        if payment.status == "paid":
            payment.action_mark_paid()
        return {"ok": True, "payment_id": payment.id}

    @http.route("/saas/api/subscription/details", type="json", auth="none", csrf=False, methods=["POST"])
    def subscription_details(self, token=None, subscription_id=None, tenant_id=None, **payload):
        if not self._check_api_key(token):
            return self._unauthorized()
        domain = [("id", "=", subscription_id)] if subscription_id else [("tenant_id", "=", tenant_id)]
        subscription = request.env["saas.subscription"].sudo().search(domain, limit=1)
        if not subscription:
            return {"ok": False, "error": "subscription_not_found"}
        return {
            "ok": True,
            "subscription": {
                "id": subscription.id,
                "tenant_id": subscription.tenant_id.id,
                "plan_id": subscription.plan_id.id,
                "billing_cycle": subscription.billing_cycle,
                "amount": subscription.amount,
                "payment_status": subscription.payment_status,
                "subscription_status": subscription.subscription_status,
                "next_billing_date": str(subscription.next_billing_date or ""),
                "auto_renew": subscription.auto_renew,
            },
        }

    def _find_tenant(self, tenant_id=None, subdomain=None):
        Tenant = request.env["saas.tenant"].sudo()
        if tenant_id:
            return Tenant.browse(tenant_id).exists()
        if subdomain:
            return Tenant.search([("subdomain", "=", subdomain)], limit=1)
        return Tenant.browse()
