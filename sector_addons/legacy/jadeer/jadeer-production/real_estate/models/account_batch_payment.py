# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta


class AccountBatchPaymentInherited(models.Model):
    _inherit = "account.batch.payment"

    unit_id = fields.Many2one('product.template', string='Unit', domain="[('state', '=', 'sold')]")
    order_id = fields.Many2one('sale.order', string='Sales Order')
    partner_id = fields.Many2one('res.partner', string='Partner')
    counter = fields.Integer(string='Counter', compute='get_payments_number')
    bank_branch = fields.Char(string='Bank Branch')
    collected_amount = fields.Monetary(string='المبلغ المحصل')
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount = fields.Float(string='Payment Amount')
    start_from = fields.Float(string='Start From', digits=(32, 2))
    partner_bank = fields.Many2one('res.bank', string='Partner Bank')
    period = fields.Selection([('monthly', 'Monthly'), ('quarter', 'Quarter'), ('yearly', 'Yearly')], default='monthly',
                              string='Period')
    state = fields.Selection([('draft', 'New'), ('post', 'Post'), ('sent', 'Sent'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False)
    # payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method', compute='_compute_payment_method',
    #                                    readonly=True, states={'draft': [('readonly', '=', False)]},
    #                                     help="The payment method used by the payments in this batch.")
    #
    # def _compute_payment_method(self):
    #     for rec in self:
    #         payment_method = self.env['ir.model.data'].search_read(
    #             [('model', '=', 'account.payment.method')])
    #         if payment_method:
    #             rec.payment_method_id = payment_method[0]['res_id']
    payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method',
                                        default=lambda self: self.env.ref('account.account_payment_method_manual_in'),
                                        readonly=True, states={'draft': [('readonly', '=', False)]},
                                        help="The payment method used by the payments in this batch.")
    genrate_payment_ids = fields.Many2many(
        'real.estate.generate.payment',
        'batch_payment_id',
        string='generated Payments',

        help="generated")
    checks_generted = fields.Boolean(copy=False,default=False)
    def action_create_payment(self):
        if self.payment_ids:
            self.payment_ids.unlink()
        type = ''
        analytic_account = False
        mon = 0
        end_date = self.date
        if self.period == 'monthly':
            mon = 1
        elif self.period == 'quarter':
            mon = 3
        elif self.period == 'yearly':
            mon = 12

        if self.batch_type == 'inbound':
            type = 'customer'
        else:
            type = 'supplier'
        if self.counter:
            amount = self.amount / self.counter
            for count in range(0, int(self.counter)):
                end_date = self.date + relativedelta(months=+(mon * count))
                payment = self.env['account.payment'].create({
                    'payment_type': self.batch_type,
                    'payment_method_id': self.payment_method_id.id,
                    'partner_type': type,
                    'partner_id': self.partner_id.id,
                    'amount': amount,
                    'currency_id': self.currency_id.id,
                    'journal_id': self.journal_id.id,
                    'batch_payment_id': self.id,
                    'payment_date': self.date,
                    'due_date': end_date,
                    'analytic_account_id': self.unit_id.product_project.id,
                    'payment_type_check': 'check',
                    'partner_bank': self.partner_bank.id,
                    'communication': str(self.start_from + count),
                    'so_id': self.order_id.id,
                })
            self._check_payments_constrains()

    @api.depends('payment_ids')
    def get_payments_number(self):
        for rec in self:
            rec.counter = len(rec.payment_ids)

    def action_create_payment_from_so(self):
        if not self.genrate_payment_ids:
            raise ValidationError('You must Generate Checks First')
        if self.payment_ids:
            self.payment_ids.unlink()
        type = ''
        analytic_account = False
        end_date = self.date
        if self.batch_type == 'inbound':
            type = 'customer'
        else:
            type = 'supplier'
        context = self.env.context.copy()
        if 'active_model' in context:
            del context['active_model']
        if 'active_id' in context:
            del context['active_id']
        if 'active_ids' in context:
            del context['active_ids']
        self.env.context = context

        if self.order_id:
            if self.order_id.order_line:
                count = 0
                for line in self.genrate_payment_ids:
                        if line.install_id.payment_state != 'paid':
                            payment = self.env['account.payment'].create({
                                'payment_type': self.batch_type,
                                'payment_method_id': self.payment_method_id.id,
                                'partner_type': type,
                                'batch_name': line.install_id.name,
                                'partner_id': self.partner_id.id,
                                'amount': line.amount,
                                'currency_id': self.currency_id.id,
                                'journal_id': self.journal_id.id,
                                'batch_payment_id': self.id,
                                'so_id': self.order_id.id,
                                'date': self.date,
                                'due_date': line.due_date,
                                'invoice_date_due': line.invoice_date_due,
                                'analytic_account_id': self.unit_id.analytic_account_id.id,
                                'payment_type_check': 'check',
                                'partner_bank': self.partner_bank.id,
                                'install_id': line.install_id.id,
                                'ref': str(int(self.start_from) + count),
                                'check_no': str(int(self.start_from) + count),
                                'other_destination_account_id': self.unit_id.project_id.property_account_receivable_id.id,

                            })

                            #from elbatal 10/10/2021
                            # if line.product_utility_ids:
                            #     payment.update(
                            #         {'other_destination_account_id': line.product_utility_ids.name.receivable_account_id.id})
                            count += 1
                self.counter = len(self.payment_ids)
            else:
                pass
    def action_generate_from_so(self):
        if self.genrate_payment_ids:
            self.genrate_payment_ids.unlink()
        type = ''
        analytic_account = False
        end_date = self.date
        if self.batch_type == 'inbound':
            type = 'customer'
        else:
            type = 'supplier'
        context = self.env.context.copy()
        if 'active_model' in context:
            del context['active_model']
        if 'active_id' in context:
            del context['active_id']
        if 'active_ids' in context:
            del context['active_ids']
        self.env.context = context

        if self.order_id:
            if self.order_id.order_line:
                count = 0
                for line in self.order_id.order_line:
                    if line.pay_type != 'reservation':
                        if line.install_inv_id.payment_state not in ('paid','partial'):
                            payment = self.env['real.estate.generate.payment'].create({
                                'payment_type': self.batch_type,
                                'payment_method_id': self.payment_method_id.id,
                                'partner_type': type,
                                'batch_name': line.install_inv_id.name,
                                'partner_id': self.partner_id.id,
                                'amount': line.price_subtotal,
                                'currency_id': self.currency_id.id,
                                'journal_id': self.journal_id.id,
                                'batch_payment_id': self.id,
                                'so_id': self.order_id.id,
                                'date': self.date,
                                'due_date': line.start_date,
                                'invoice_date_due': line.start_date,
                                'analytic_account_id': self.unit_id.analytic_account_id.id,
                                'payment_type_check': 'check',
                                'partner_bank': self.partner_bank.id,
                                'install_id': line.install_inv_id.id,
                                'ref': str(int(self.start_from) + count),
                                'check_no': str(int(self.start_from) + count),

                            })
                            self.write({'genrate_payment_ids': [(4, payment.id)]})

                            #from elbatal 10/10/2021
                            # if line.product_utility_ids:
                            #     payment.update(
                            #         {'other_destination_account_id': line.product_utility_ids.name.receivable_account_id.id})
                            count += 1
                self.counter = len(self.payment_ids)
                self.write({'checks_generted':True})
            else:
                pass
    def action_post_payment(self):
        context = self.env.context.copy()
        if 'active_model' in context:
            del context['active_model']
        if 'active_id' in context:
            del context['active_id']
        if 'active_ids' in context:
            del context['active_ids']
        self.env.context = context
        for line in self.payment_ids:
            if line.state == 'draft':
                line.action_post()
        self.state = 'post'

    def validate_batch(self):
        records = self.filtered(lambda x: x.state == 'post')
        for record in records:
            record.payment_ids.write({'state': 'posted', 'payment_reference': record.name})
        records.write({'state': 'sent'})

        records = self.filtered(lambda x: x.file_generation_enabled)
        if records:
            return self.export_batch_payment()

    # @api.constrains('batch_type', 'journal_id', 'payment_ids')
    def _check_payments_constrains(self):
        for record in self:
            all_companies = set(record.payment_ids.mapped('company_id'))
            if len(all_companies) > 1:
                raise ValidationError(_("All payments in the batch must belong to the same company."))
            all_journals = set(record.payment_ids.mapped('journal_id'))
            if len(all_journals) > 1 or record.payment_ids[0].journal_id != record.journal_id:
                raise ValidationError(
                    _("The journal of the batch payment and of the payments it contains must be the same."))
            all_types = set(record.payment_ids.mapped('payment_type'))
            if len(all_types) > 1:
                raise ValidationError(_("All payments in the batch must share the same type."))
            if all_types and record.batch_type not in all_types:
                raise ValidationError(_("The batch must have the same type as the payments it contains."))
            all_payment_methods = set(record.payment_ids.mapped('payment_method_id'))
            if len(all_payment_methods) > 1:
                raise ValidationError(_("All payments in the batch must share the same payment method."))
            if all_payment_methods and record.payment_method_id not in all_payment_methods:
                raise ValidationError(_("The batch must have the same payment method as the payments it contains."))

    @api.onchange('unit_id', 'order_id')
    def onchange_unit_id(self):
        for line in self:
            if line.order_id:
                line.partner_id = line.order_id.partner_id
                line.unit_id = line.order_id.unit_id
                line.amount = line.order_id.amount_total
                line.batch_type = 'inbound'
            if line.unit_id:
                line.partner_id = line.unit_id.customer_id

# class real_state_change(models.Model):
#     _name = 'real.state.prepayment'
#
#     payment_type = fields.Selection([
#         ('outbound', 'Send'),
#         ('inbound', 'Receive'),
#     ], string='Payment Type', default='inbound', required=True, tracking=True)
#     partner_type = fields.Selection([
#         ('customer', 'Customer'),
#         ('supplier', 'Vendor'),
#     ], default='customer', tracking=True, required=True)
#
#     payment_method_id = fields.Many2one(
#         related='payment_method_line_id.payment_method_id',
#         string="Method",
#         tracking=True,
#         store=True
#     )
#     batch_name = fields.Char('Name')
#     partner_id = fields.Many2one(
#         comodel_name='res.partner',
#         string="Customer/Vendor",
#         store=True, readonly=False, ondelete='restrict',
#         domain="['|', ('parent_id','=', False), ('is_company','=', True)]",
#         tracking=True,
#         check_company=True)
#     currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
#       )
#     amount = fields.Monetary(currency_field='currency_id')
#     journal_id = fields.Many2one('account.journal', string="Journal")
#     batch_payment_id = fields.Many2one(string='Batch Payment',
#                                  comodel_name='account.batch.payment',
#                                  help="Batch payment from which the file has been generated.")
#     so_id = fields.Many2one('sale.order', string='Sale Order')

class realStateGenratePayment(models.Model):
    _name = 'real.estate.generate.payment'
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)

    payment_method_id = fields.Many2one(
        string='Payment Method',
        comodel_name='account.payment.method',
    )
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], store=True, copy=False,
        )
    batch_name = fields.Char('Batch Transfer Name', readonly=True)
    partner_id = fields.Many2one('res.partner')
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
        )
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The payment's currency.")
    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.source_currency_id or wizard.company_id.currency_id
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
       )
    batch_payment_id = fields.Many2one(string='Batch Payment',
                                 comodel_name='account.batch.payment',
                                 readonly=True,
                                 help="Batch payment from which the file has been generated.")
    so_id = fields.Many2one('sale.order', string='Sale Order')
    date = fields.Date(
        string='Date',
        index=True,
        readonly=True,
        copy=False,
        tracking=True,
        default=fields.Date.context_today
    )
    due_date = fields.Date(string='Due Date')
    invoice_date_due = fields.Date(string='Due Date', readonly=True, index=True, copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)
    payment_type_check = fields.Selection([
        ('payment', "Payment"),
        ('check', "Cheque"),
    ], default='payment', required=True, string='Payment Method')
    partner_bank = fields.Many2one('res.bank', string='Partner Bank')
    install_id = fields.Many2one(comodel_name="account.move",string='Installment')

    ref = fields.Char(string='Reference', copy=False, tracking=True)
    check_no = fields.Char('Check No.')
