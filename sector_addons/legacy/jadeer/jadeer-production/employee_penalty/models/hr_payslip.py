""" Initialize Hr Payroll """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    penalty_amount = fields.Float(
        compute='_compute_penalty_amount',
        store=1
    )
    penalty_ids = fields.Many2many(
        'employee.penalty'
    )

    @api.depends('penalty_ids')
    def _compute_penalty_amount(self):
        """ Compute penalty_amount value """
        for rec in self:
            total = 0
            for pen in rec.penalty_ids:
                total += pen.penalty_amount
            rec.penalty_amount = total

    @api.onchange('employee_id', 'contract_id', 'date_from',
                  'date_to')
    def _onchange_employee(self):
        # super(HrPayslip, self)._onchange_employee()
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        if employee and date_from and date_to:
            penalties = employee.penalty_ids.filtered(
                lambda l: not l.deducted and date_from <= l.date <= date_to and l.state == 'approve')
            self.penalty_ids = penalties.ids

    def action_payslip_done(self):
        for pen in self.penalty_ids:
            pen.deducted = True
        return super(HrPayslip, self).action_payslip_done()
