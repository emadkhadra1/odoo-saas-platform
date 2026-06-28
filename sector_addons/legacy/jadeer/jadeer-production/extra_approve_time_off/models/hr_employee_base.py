""" Initialize Hr Employee Base """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrEmployeeBase(models.AbstractModel):
    """
        Inherit Hr Employee Base:
         -
    """
    _inherit = 'hr.employee.base'

    current_leave_state = fields.Selection(selection_add=
        [('validate2', 'Validate2')]
    )
