""" Initialize Hr Employee """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrEmployee(models.Model):
    """
        Inherit Hr Employee:
         - 
    """
    _inherit = 'hr.employee'
    
    manager_time_off = fields.Many2one(
        'res.users'
    )
