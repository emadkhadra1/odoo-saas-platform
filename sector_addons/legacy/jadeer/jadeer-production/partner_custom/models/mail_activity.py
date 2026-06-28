from odoo import api, fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    department_id = fields.Many2one(comodel_name="hr.department",)
    type = fields.Selection(selection=[('request', 'Request'), ('complain', 'Complain'),
                                                  ('inquery','Inquery')])