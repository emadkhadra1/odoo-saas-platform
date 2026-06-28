# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields,_
from odoo.exceptions import UserError


class HrLoanAcc(models.Model):
    _inherit = 'hr.loan'

    employee_account_id = fields.Many2one('account.account', string="Loan Account")
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    manager_id = fields.Many2one('res.users', string='Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    hr_manager_id = fields.Many2one('res.users', string='HR Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    cfo_manager_id = fields.Many2one('res.users', string='CFO Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    ceo_manager_id = fields.Many2one('res.users', string='CEO Manager',compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True,)
    current_user = fields.Many2one('res.users', compute='_compute_current_user')
    same_user = fields.Boolean(compute='_compute_current_user')

    def _compute_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
            rec.same_user = False
            if rec.state == 'waiting_approval_1':
                if rec.manager_id == self.env.user:
                    rec.same_user = True
                else:
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

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for sheet in self:
            sheet.manager_id = sheet.employee_id.parent_id.user_id.id
            sheet.hr_manager_id = sheet.env.company.loan_hr_manager_id.id
            sheet.cfo_manager_id = sheet.env.company.loan_cfo_manager_id.id
            sheet.ceo_manager_id = sheet.env.company.loan_ceo_manager_id.id

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Manager Approval'),
        ('waiting_hr_approval', 'HR Approval'),
        ('waiting_approval_cfo', 'CFO Approval'),
        ('waiting_approval_ceo', 'CEO Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )
    def action_loan_pay(self):
        unpaid_amount = sum([line.amount for line in self.loan_lines if not line.paid])
        return {
            'context': {'default_unpaid_amount': unpaid_amount,
                        'default_loan_id': self.id},
            'name': 'Pay Loan',
            'res_model': 'register.loan.payment',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('ohrms_loan_accounting.register_loan_payment_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    def manager_approve_request(self):

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no request to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['waiting_approval_1'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'waiting_hr_approval', 'manager_id' :self.env.user.id})
        notification['params'].update({
            'title': _('The request were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        return notification
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
        for sheet in filtered_sheet:
            sheet.action_double_approve()
            sheet.write({'ceo_manager_id' :self.env.user.id})

        notification['params'].update({
            'title': _('The request were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        return notification
    def action_approve(self):
        """This create account move for request.
            """
        loan_approve = self.env['ir.config_parameter'].sudo().get_param('account.loan_approve')
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise UserError('You must Define a contract for employee')
        if not self.loan_lines:
            raise UserError('You must compute installment before Approved')
        if loan_approve:
            self.write({'state': 'waiting_approval_2'})
        else:
            if not self.employee_account_id or not self.treasury_account_id or not self.journal_id:
                raise UserError("You must enter employee account & Treasury account and journal to approve ")
            if not self.loan_lines:
                raise UserError('You must compute Loan Request before Approved')
            timenow = time.strftime('%Y-%m-%d')
            for loan in self:
                amount = loan.loan_amount
                loan_name = loan.employee_id.name
                reference = loan.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.employee_account_id.id
                credit_account_id = loan.treasury_account_id.id
                debit_vals = {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'partner_id': loan.employee_id.address_id.id,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'loan_id': loan.id,
                }
                credit_vals = {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'partner_id': loan.employee_id.address_id.id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'loan_id': loan.id,
                }
                vals = {
                    'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'partner_id': loan.employee_id.address_id.id,
                    'date': timenow,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                move.post()

                #####    CREATE Reverse account.move for diff (PAID Lines) , To Prevent Duplicate Entries in Reschedule Cases #####
                # if loan.original_loan_id:
                #     not_paid_amount = 0
                #     for l in loan.original_loan_id.loan_lines:
                #         if not l.paid:
                #             not_paid_amount += l.amount
                #     debit_vals = {
                #         'name': loan_name,
                #         'account_id': credit_account_id,
                #         'journal_id': journal_id,
                #         'date': timenow,
                #         'partner_id': loan.employee_id.address_id.id,
                #         'debit': not_paid_amount > 0.0 and not_paid_amount or 0.0,
                #         'credit': not_paid_amount < 0.0 and -not_paid_amount or 0.0,
                #         'loan_id': loan.id,
                #     }
                #     credit_vals = {
                #         'name': loan_name,
                #         'account_id': debit_account_id,
                #         'journal_id': journal_id,
                #         'date': timenow,
                #         'partner_id': loan.employee_id.address_id.id,
                #         'debit': not_paid_amount < 0.0 and -not_paid_amount or 0.0,
                #         'credit': not_paid_amount > 0.0 and not_paid_amount or 0.0,
                #         'loan_id': loan.id,
                #     }
                #     vals = {
                #         'narration': loan_name,
                #         'ref': reference,
                #         'journal_id': journal_id,
                #         'partner_id': loan.employee_id.address_id.id,
                #         'date': timenow,
                #         'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                #     }
                #     reverse_move = self.env['account.move'].create(vals)
                #     reverse_move.post()
            super(HrLoanAcc, self).action_approve()
        return True

    def action_double_approve(self):
        """This create account move for request in case of double approval.
            """
        if not self.employee_account_id or not self.treasury_account_id or not self.journal_id:
            raise UserError("You must enter employee account & Treasury account and journal to approve ")
        if not self.loan_lines:
            raise UserError('You must compute Loan Request before Approved')
        timenow = time.strftime('%Y-%m-%d')
        for loan in self:
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            debit_account_id = loan.employee_account_id.id
            credit_account_id = loan.treasury_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': loan.employee_id.address_id.id,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': loan.employee_id.address_id.id,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_id.id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()

            #####    CREATE Reverse account.move for diff (PAID Lines) , To Prevent Duplicate Entries in Reschedule Cases #####
            # if loan.original_loan_id:
            #     not_paid_amount = 0
            #     for l in loan.original_loan_id.loan_lines:
            #         if not l.paid:
            #             not_paid_amount += l.amount
            #     debit_vals = {
            #         'name': loan_name,
            #         'account_id': credit_account_id,
            #         'journal_id': journal_id,
            #         'date': timenow,
            #         'partner_id': loan.employee_id.address_id.id,
            #         'debit': not_paid_amount > 0.0 and not_paid_amount or 0.0,
            #         'credit': not_paid_amount < 0.0 and -not_paid_amount or 0.0,
            #         'loan_id': loan.id,
            #     }
            #     credit_vals = {
            #         'name': loan_name,
            #         'account_id': debit_account_id,
            #         'journal_id': journal_id,
            #         'date': timenow,
            #         'partner_id': loan.employee_id.address_id.id,
            #         'debit': not_paid_amount < 0.0 and -not_paid_amount or 0.0,
            #         'credit': not_paid_amount > 0.0 and not_paid_amount or 0.0,
            #         'loan_id': loan.id,
            #     }
            #     vals = {
            #         'narration': loan_name,
            #         'ref': reference,
            #         'journal_id': journal_id,
            #         'partner_id': loan.employee_id.address_id.id,
            #         'date': timenow,
            #         'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            #     }
            #     reverse_move = self.env['account.move'].create(vals)
            #     reverse_move.post()
        self.write({'state': 'approve'})
        # if self.original_loan_id:
        #     for line in self.original_loan_id.loan_lines:
        #         line.paid = True
        return True

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                total_paid += line.paid_amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid


class HrLoanLineAcc(models.Model):
    _inherit = "hr.loan.line"

    paid_amount = fields.Float(string="Paid Amount", required=False, )
    paid = fields.Boolean(string="Paid", help="Paid",store=True,compute="_compute_paid_amount")

    @api.depends('paid_amount')
    def _compute_paid_amount(self):
        for rec in self:
            if rec.paid_amount == rec.amount:
                rec.paid = True
    def action_paid_amount(self):
        """This create the account move line for payment of each installment.
            """
        timenow = time.strftime('%Y-%m-%d')
        for line in self:
            if line.loan_id.state != 'approve':
                raise UserError("Loan Request must be approved")
            amount = line.amount - line.paid_amount
            loan_name = line.employee_id.name
            reference = line.loan_id.name
            journal_id = line.loan_id.journal_id.id
            debit_account_id = line.loan_id.treasury_account_id.id
            credit_account_id = line.loan_id.employee_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'partner_id': line.loan_id.employee_id.address_id.id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': line.loan_id.employee_id.address_id.id,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'partner_id': line.loan_id.employee_id.address_id.id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
            line.paid_amount = amount
        return True


class HrPayslipAcc(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def do_employee_loan(self):
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        payslip_input_type_id = self.env.ref('ohrms_loan.hr_payslip_input_type_loan')
        if date_from and date_to and employee and payslip_input_type_id:
            lon_obj = self.env['hr.loan'].search([('employee_id', '=', employee.id), ('state', '=', 'approve')])
            total_loan = 0.0
            lst_loans = []
            for loan in lon_obj:
                for loan_line in loan.loan_lines:
                    if date_from <= loan_line.date <= date_to and not loan_line.paid:
                        total_loan += loan_line.amount - loan_line.paid_amount
                        lst_loans.append((6, 0, loan_line.ids))
            updated = False
            x = lst_loans
            if self.input_line_ids:
                for input_line in self.input_line_ids:
                    if payslip_input_type_id == input_line.input_type_id:
                        input_line.amount = total_loan
                        input_line.loan_line_id = lst_loans
                        updated = True
            if not updated:
                self.input_line_ids = [(0, 0, {
                    'input_type_id': payslip_input_type_id.id,
                    'loan_line_id': lst_loans,
                    'amount': total_loan,
                })]
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        super(HrPayslipAcc, self)._onchange_employee()
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        payslip_input_type_id = self.env.ref('ohrms_loan.hr_payslip_input_type_loan')
        if date_from and date_to and employee and payslip_input_type_id:
            lon_obj = self.env['hr.loan'].search([('employee_id', '=', employee.id), ('state', '=', 'approve')])
            total_loan = 0.0
            lst_loans = []
            for loan in lon_obj:
                for loan_line in loan.loan_lines:
                    if date_from <= loan_line.date <= date_to and not loan_line.paid:
                        total_loan += loan_line.amount - loan_line.paid_amount
                        lst_loans.append((6, 0, loan_line.ids))
            updated = False
            x = lst_loans
            if self.input_line_ids:
                for input_line in self.input_line_ids:
                    if payslip_input_type_id == input_line.input_type_id:
                        input_line.amount = total_loan
                        input_line.loan_line_id = lst_loans
                        updated = True
            if not updated:
                self.input_line_ids = [(0, 0, {
                    'input_type_id': payslip_input_type_id.id,
                    'loan_line_id': lst_loans,
                    'amount': total_loan,
                })]

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.action_paid_amount()
                if line.amount >= line.loan_line_id.amount:
                    line.loan_line_id.paid = True
                    line.loan_line_id.paid_amount = line.amount
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslipAcc, self).action_payslip_done()
