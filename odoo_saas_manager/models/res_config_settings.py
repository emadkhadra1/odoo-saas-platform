from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    saas_template_database = fields.Char(config_parameter="saas_manager.template_database")
    saas_public_domain = fields.Char(config_parameter="saas_manager.public_domain", default="mycompany.com")
    saas_api_key = fields.Char(config_parameter="saas_manager.api_key", groups="odoo_saas_manager.group_saas_admin")
