""" Initialize Hr Contract """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrContract(models.Model):
    """
        Inherit Hr Contract:
         -
    """
    _inherit = 'hr.contract'

    no_month_days = fields.Float(default=30)
    hour_value = fields.Float()
    day_value = fields.Float(compute='_compute_day_value')
    workday_hours = fields.Float(default=8)
    start_training = fields.Date("Start training")
    end_training = fields.Date("End training")


    def set_wage(self):
        print("Set Wage")

    @api.depends('wage', 'no_month_days','workday_hours')
    def _compute_day_value(self):
        """ Compute day_value value """
        for rec in self:
            rec.day_value = rec.wage / rec.no_month_days if rec.no_month_days > 0 else 0
            rec.hour_value = rec.wage / rec.no_month_days / rec.workday_hours if rec.no_month_days > 0 else 0


