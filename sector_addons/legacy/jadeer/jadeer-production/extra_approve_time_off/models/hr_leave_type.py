""" Initialize Hr Leave Type """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrLeaveType(models.Model):
    """
        Inherit Hr Leave Type:
         - 
    """
    _inherit = 'hr.leave.type'

    extra_approve = fields.Boolean()

