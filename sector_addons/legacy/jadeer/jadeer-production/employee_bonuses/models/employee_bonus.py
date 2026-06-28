""" Initialize Employee bonuses """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning

class EmployeePenalty(models.Model):
    _name = 'employee.bonus.type'
    name = fields.Char("Name")


class EmployeeBonus(models.Model):
    """
        Initialize Employee bonuses:
         -
    """
    _name = 'employee.bonus'
    _description = 'Employee Bonuses'
    _rec_name = 'employee_id'

    type = fields.Many2one("employee.bonus.type")
    employee_id = fields.Many2one(
        'hr.employee',
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1),
    )
    pin = fields.Char(related="employee_id.pin")
    bonus_amount = fields.Float(
        compute='_compute_bonus_amount'
    )
    bonus_type = fields.Selection(
        [('hour', 'Hour'),
         ('day', 'Day'),
         ('fixed', 'Fixed')],
        default='hour',
    )
    date = fields.Date(default=fields.Date.today())
    bonus_value = fields.Float()
    contract_id = fields.Many2one(
        'hr.contract',
        related='employee_id.contract_id'
    )
    reason = fields.Html()
    deducted = fields.Boolean(
        readonly=1
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approve', 'Approved'),
         ('cancel', 'Canceled')],
        default='draft',
        string='Status'
    )
    # manager_time_off = fields.Many2one(
    #     related='employee_id.manager_time_off'
    # )
    manager_time_off_there = fields.Boolean(
    )
    parent_there = fields.Boolean(
    )

    @api.depends('employee_id')
    def _compute_manager_time_off_there(self):
        """ Compute manager_time_off_there value """
        for rec in self:
            if rec.employee_id.manager_time_off.id == self.env.user.id:
                rec.manager_time_off_there = True
            if rec.employee_id.parent_id.id == self.env.user.id:
                rec.parent_there = True
            else:
                rec.manager_time_off_there = False
                rec.parent_there = False

    # def action_first_approve(self):
    #     """ Action First Approve """
    #     self.write({
    #         'state': 'first_approve'
    #     })

    def action_approve(self):
        """ Action Second Approve """
        self.write({
            'state': 'approve'
        })

    def action_set_draft(self):
        """ Action Set Draft Approve """
        self.write({
            'state': 'draft'
        })

    def action_cancel(self):
        """ Action Cancel """
        self.write({
            'state': 'cancel'
        })

    @api.depends('bonus_type', 'contract_id', 'bonus_value')
    def _compute_bonus_amount(self):
        """ Compute bonus_amount value """
        for rec in self:
            if rec.employee_id and rec.contract_id and rec.env.user.company_id.no_month_days:
                if rec.bonus_type == 'hour':
                    rec.bonus_amount = rec.bonus_value * rec.contract_id.hour_value
                elif rec.bonus_type == 'day':
                    rec.bonus_amount = rec.bonus_value * rec.contract_id.day_value
                elif rec.bonus_type == 'fixed':
                    rec.bonus_amount = rec.bonus_value

                else:
                    rec.bonus_amount = 0
            else:
                rec.bonus_amount = 0
