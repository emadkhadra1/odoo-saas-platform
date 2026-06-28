from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError, Warning
from dateutil.relativedelta import relativedelta


class Loan(models.Model):
    _name = 'loan.type'
    _rec_name = 'name'

    name = fields.Char()
    factor = fields.Float(default=1)


class LoanRescudeled(models.Model):
    _name = 'loan.reschedule.request'
    _rec_name = 'loan_id'
    amount = fields.Float(string="Updated Amount", required=True, )
    old_amount = fields.Float(string="Old Amount",store=True,compute="action_compute_old_amount" )
    loan_line_id = fields.Many2one(comodel_name="hr.loan.line")
    loan_id = fields.Many2one(comodel_name="hr.loan")
    new_date = fields.Date(string="Date")
    is_last_installment = fields.Boolean(related="loan_line_id.is_last_installment")
    update_type = fields.Selection(string="Update Type", selection=[('amount', 'Amount'), ('date', 'Date'), ],
                                   required=True, default='amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_hr_approval', 'HR Approval'),
        ('waiting_approval_cfo', 'CFO Approval'),
        ('waiting_approval_ceo', 'CEO Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )


    hr_manager_id = fields.Many2one('res.users', string='HR Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    cfo_manager_id = fields.Many2one('res.users', string='CFO Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    ceo_manager_id = fields.Many2one('res.users', string='CEO Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    current_user = fields.Many2one('res.users', compute='_compute_current_user')
    same_user = fields.Boolean(compute='_compute_current_user')

    @api.depends('loan_line_id')
    def action_compute_old_amount(self):
        for rec in self:
            if rec.loan_line_id:
                rec.old_amount = rec.loan_line_id.amount

    def action_submit(self):
        for rec in self:
            rec.write({'state':'waiting_hr_approval'})
    def _compute_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
            rec.same_user = False
            if rec.state == 'waiting_hr_approval':
                if rec.hr_manager_id == self.env.user:
                    rec.same_user = True
                else:
                    rec.same_user = False
            if rec.state == 'waiting_approval_cfo':

                if rec.cfo_manager_id == self.env.user :
                    rec.same_user = True
                else:
                    rec.same_user = False
            if rec.state == 'waiting_approval_ceo':

                if rec.ceo_manager_id == self.env.user :
                    rec.same_user = True
                else:
                    rec.same_user = False

    @api.depends('loan_id')
    def _compute_from_employee_id(self):
        for sheet in self:
            sheet.hr_manager_id = sheet.env.company.loan_hr_manager_id.id
            sheet.cfo_manager_id = sheet.env.company.loan_cfo_manager_id.id
            sheet.ceo_manager_id = sheet.env.company.loan_ceo_manager_id.id

    def hr_manager_approve_request(self):

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no request to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['waiting_hr_approval'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'waiting_approval_cfo', 'hr_manager_id' :self.env.user.id})
        notification['params'].update({
            'title': _('The request were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        return notification
    def cfo_manager_approve_request(self):

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no request to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['waiting_approval_cfo'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'waiting_approval_ceo', 'ceo_manager_id' :self.env.user.id})
        notification['params'].update({
            'title': _('The request were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        return notification
    def ceo_manager_approve_request(self):

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no request to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['waiting_approval_ceo'])
        if not filtered_sheet:
            return notification
        if self.update_type == 'amount':
            self.update_amount()
        else:
            self.update_date()
        for sheet in filtered_sheet:
            sheet.write({'state':'approve','ceo_manager_id' :self.env.user.id})

        notification['params'].update({
            'title': _('The request were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        return notification
    def update_amount(self):
        diff = self.old_amount - self.amount
        index = 0
        for line in self.loan_id.loan_lines:
            index += 1
            if line == self.loan_line_id:
                line.amount = self.amount
                break
        try:
            line_diff = diff / (len(self.loan_id.loan_lines) - index)
            for i, line_loan in enumerate(self.loan_id.loan_lines):
                if i >= index:
                    line_loan.amount += line_diff
        except:
            raise ValidationError("Last Installment ! You Can Change The Payment Date")

    def update_date(self):
        day_num = self.new_date.day
        if self.loan_line_id.date != self.new_date:
            for line in self.loan_id.loan_lines.filtered(lambda x: x.date > self.loan_line_id.date):
                line.date = line.date.replace(day=day_num) + relativedelta(months=1)

            self.loan_line_id.date = self.new_date
            self.loan_id.is_rescheduled = True

