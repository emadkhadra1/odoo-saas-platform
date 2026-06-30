from odoo import api, fields, models


class Country(models.Model):
    _inherit = 'res.country'

    num_phone_digit = fields.Integer(string="# Phone Digits")
