import json
from pathlib import Path

from odoo import http
from odoo.http import request
from markupsafe import escape
from werkzeug.wrappers import Response


class OdooSaasWebsiteController(http.Controller):
    """Expose the interactive SaaS presentation through an Odoo website URL."""

    _preview_dir = Path(__file__).resolve().parents[1] / "static" / "preview"
    _asset_base = "/odoo_saas_website/static/preview/"
    _asset_version = "19.0.1.2.1"

    def _render_preview(self, filename="index.html"):
        html = (self._preview_dir / filename).read_text(encoding="utf-8")
        html = html.replace('href="styles.css"', f'href="{self._asset_base}styles.css?v={self._asset_version}"')
        html = html.replace('src="script.js"', f'src="{self._asset_base}script.js?v={self._asset_version}"')
        html = html.replace('src="assets/', f'src="{self._asset_base}assets/')
        return request.make_response(
            html,
            headers=[
                ("Content-Type", "text/html; charset=utf-8"),
                ("Cache-Control", "no-store"),
            ],
        )

    @http.route(["/", "/index.html", "/saas-platform"], type="http", auth="public", website=True, sitemap=True)
    def saas_platform(self, **kwargs):
        return self._render_preview()

    @http.route(["/en", "/index-en.html", "/en/saas-platform"], type="http", auth="public", website=True, sitemap=True)
    def saas_platform_en(self, **kwargs):
        return self._render_preview("index-en.html")

    @http.route(
        [
            "/solution-construction.html",
            "/solutions/construction",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_construction(self, **kwargs):
        return self._render_preview("solution-construction.html")

    @http.route(
        [
            "/solution-construction-en.html",
            "/en/solutions/construction",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_construction_en(self, **kwargs):
        return self._render_preview("solution-construction-en.html")

    @http.route(
        [
            "/solution-realestate.html",
            "/solutions/real-estate",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_realestate(self, **kwargs):
        return self._render_preview("solution-realestate.html")

    @http.route(
        [
            "/solution-realestate-en.html",
            "/en/solutions/real-estate",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_realestate_en(self, **kwargs):
        return self._render_preview("solution-realestate-en.html")

    @http.route(
        [
            "/solution-hr.html",
            "/solutions/hr",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_hr(self, **kwargs):
        return self._render_preview("solution-hr.html")

    @http.route(
        [
            "/solution-hr-en.html",
            "/en/solutions/hr",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_hr_en(self, **kwargs):
        return self._render_preview("solution-hr-en.html")

    @http.route(
        [
            "/solution-3pl.html",
            "/solutions/3pl",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_3pl(self, **kwargs):
        return self._render_preview("solution-3pl.html")

    @http.route(
        [
            "/solution-3pl-en.html",
            "/en/solutions/3pl",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_3pl_en(self, **kwargs):
        return self._render_preview("solution-3pl-en.html")

    @staticmethod
    def _json_response(payload, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=status,
            content_type="application/json; charset=utf-8",
        )

    @http.route(
        "/saas-platform/crm-lead",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
        website=True,
    )
    def create_crm_lead(self, **kwargs):
        payload = request.httprequest.get_json(silent=True) or kwargs
        contact_name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip()
        sector = (payload.get("solution") or "").strip()
        message = (payload.get("message") or "").strip()

        if not contact_name or not email:
            return self._json_response(
                {"ok": False, "error": "name_email_required"},
                status=400,
            )

        lead_model = request.env["crm.lead"].sudo()
        description_lines = [
            ("مصدر الطلب", "Qimam Solutions Cloud website"),
            ("القطاع", sector),
            ("ملاحظات", message),
            ("الرابط", request.httprequest.referrer or request.httprequest.url),
        ]
        description = "<br/>".join(
            f"<strong>{escape(label)}:</strong> {escape(value)}"
            for label, value in description_lines
            if value
        )

        values = {
            "name": f"SaaS Demo - {contact_name} - {sector or 'Website'}",
            "contact_name": contact_name,
            "email_from": email,
            "description": description,
            "type": "opportunity",
        }
        values = {
            field_name: field_value
            for field_name, field_value in values.items()
            if field_name in lead_model._fields and field_value
        }
        lead = lead_model.create(values)
        return self._json_response({"ok": True, "lead_id": lead.id})
