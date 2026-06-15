from odoo import http
from odoo.http import request


class OdooSaasWebsiteController(http.Controller):
    """Expose the interactive SaaS presentation through an Odoo website URL."""

    @http.route("/saas-platform", type="http", auth="public", website=True, sitemap=True)
    def saas_platform(self, **kwargs):
        return request.redirect("/odoo_saas_website/static/preview/index.html")
