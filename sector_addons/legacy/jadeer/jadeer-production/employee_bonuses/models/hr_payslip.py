""" Initialize Hr Payroll """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    bonus_amount = fields.Float(
        compute='_compute_bonus_amount',
        store=1
    )
    bonus_ids = fields.Many2many(
        'employee.bonus'
    )

    @api.depends('bonus_ids')
    def _compute_bonus_amount(self):
        """ Compute bonus_amount value """
        for rec in self:
            total = 0
            for bon in rec.bonus_ids:
                total += bon.bonus_amount
            rec.bonus_amount = total

    @api.onchange('employee_id', 'contract_id', 'date_from',
                  'date_to')
    def _onchange_employee_bonuses(self):
        # super(HrPayslip, self)._onchange_employee()
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        if employee and date_from and date_to:
            bonuses = employee.bonus_ids.filtered(
                lambda l: not l.deducted and date_from <= l.date <= date_to and l.state == 'approve')
            self.bonus_ids = bonuses.ids

    def action_payslip_done(self):
        for bon in self.bonus_ids:
            bon.deducted = True
        return super(HrPayslip, self).action_payslip_done()
