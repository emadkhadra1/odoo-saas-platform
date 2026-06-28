# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import ValidationError, UserError


class ProductCede(models.Model):
    _name = 'product.cede'

    product_id = fields.Many2one('product.template')
    customer_id = fields.Many2one('res.partner', required=True, string='Property Customer')
    attachment_id = fields.Many2many('ir.attachment', 'class_ir_attachments', 'class_id1', 'attachment_id1',
                                     'Attachments', store=True)

    def action_cede_button(self):
        invoice_ids = self.env['account.move'].search([('state', '=', 'posted'), ('unit_id', '=', self.product_id.id),
                                                          ('partner_id', '=', self.product_id.customer_id.id)])

        for invoice in invoice_ids:
            invoice.move_id.reverse_moves(date=datetime.datetime.now())
            invoice_id = self.env['account.move'].create({
                'sale_order': invoice.sale_order.id,
                'unit_id': invoice.unit_id.id,
                'partner_id': self.customer_id.id,
                'analytic_account_id': invoice.analytic_account_id.id,
                'account_id': self.customer_id.property_account_receivable_id.id,
                'invoice_date_due': invoice.invoice_date_due,
                'invoice_date': invoice.invoice_date_due,
                'date_temp': invoice.invoice_date_due,
                'type': 'out_invoice',
                'state': 'draft',
            })
            account_id = ""
            if invoice.unit_id.id:
                account_id = invoice.unit_id.property_account_income_id.id or invoice.unit_id.categ_id.property_account_income_categ_id.id
            if not account_id:
                raise UserError(
                    _(
                        'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                    (invoice.unit_id.product_variant_id.name,))

            if invoice.unit_id.min_deposit_amount == 0:
                raise UserError(
                    _(
                        'Please add Min Deposit Amount For Unit "%s"') %
                    (self.unit_id.name,))
            for line in invoice.invoice_line_ids:
                invoice_line_ids = self.env['account.move.line'].create({
                    'name': str(invoice.name) + ' / ' + str(self.customer_id.name),
                    'move_id': invoice_id.id,
                    'account_id': account_id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                })
            invoice.state = 'cancel'

        if self.product_id:
            self.product_id.customer_id = self.customer_id
            self.product_id.hold_date = False
            self.product_id.booked_date = False
            if self.product_id.requset_id:
                self.product_id.requset_id.active = False
                self.product_id.requset_id = False
            if self.product_id.analytic_account_id:
                self.product_id.analytic_account_id.partner_id = self.customer_id
            history_line_ids = self.env['product.history'].create({
                'product_id': self.product_id.id,
                'state': 'waiver',
                'confirm_date': datetime.datetime.now(),
                'attachment_id': [(6, 0, self.attachment_id.ids)],
            })
