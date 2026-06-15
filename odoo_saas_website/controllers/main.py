from pathlib import Path

from odoo import http
from odoo.http import request


class OdooSaasWebsiteController(http.Controller):
    """Expose the interactive SaaS presentation through an Odoo website URL."""

    _preview_dir = Path(__file__).resolve().parents[1] / "static" / "preview"
    _asset_base = "/odoo_saas_website/static/preview/"

    def _render_preview(self):
        html = (self._preview_dir / "index.html").read_text(encoding="utf-8")
        html = html.replace('href="styles.css"', f'href="{self._asset_base}styles.css"')
        html = html.replace('src="script.js"', f'src="{self._asset_base}script.js"')
        html = html.replace('src="assets/', f'src="{self._asset_base}assets/')
        return request.make_response(
            html,
            headers=[
                ("Content-Type", "text/html; charset=utf-8"),
                ("Cache-Control", "no-store"),
            ],
        )

    @http.route(["/", "/saas-platform"], type="http", auth="public", website=True, sitemap=True)
    def saas_platform(self, **kwargs):
        return self._render_preview()
