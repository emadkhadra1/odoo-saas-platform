""" Initialize Hr Employee """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrEmployee(models.AbstractModel):
    """
        Inherit Hr Employee:
         -
    """
    _inherit = 'hr.employee.base'

    bonus_ids = fields.One2many(
        'employee.bonus',
        'employee_id'
    )
