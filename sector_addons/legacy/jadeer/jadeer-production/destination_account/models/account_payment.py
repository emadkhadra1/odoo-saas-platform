# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticAccountInherited(models.Model):
    _inherit = "account.analytic.account"

    # is_unit_project = fields.Boolean(default=False)
    is_project = fields.Boolean(string="Project", )
    # penalty_percentage = fields.Float(string='Penalty Percentage')
    property_account_receivable_id = fields.Many2one('account.account', string='Receivable Account', domain=lambda x: [
        ('user_type_id', '=', x.env.ref('account.data_account_type_receivable').id)], company_dependent=True)


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    destination_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Destination Journal',
        domain="[('type', 'in', ('bank','cash')), ('id', '!=', journal_id)]",

    )
    other_destination_account_id = fields.Many2one('account.account', string='Destination Account')
    # @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id', 'other_destination_account_id')
    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'other_destination_account_id')
    def _compute_destination_account_id(self):
        for payment in self:
            if payment.other_destination_account_id:
                payment.destination_account_id = payment.other_destination_account_id.id
            else:
                super(AccountPayment, self)._compute_destination_account_id()

    @api.onchange('invoice_ids', 'payment_type', 'partner_type', 'partner_id','type_of_check')
    def _onchange_other_destination_account_id(self):
        # if self.invoice_ids:
        #     self.destination_account_id = self.invoice_ids[0].account_id.id

        if self.partner_type == 'customer' and self.payment_type == 'inbound':
            self.other_destination_account_id = self.partner_id.property_account_receivable_id.id

        elif self.partner_type == 'customer' and self.payment_type == 'outbound':
            self.other_destination_account_id = self.partner_id.property_account_payable_id.id

        elif self.partner_type == 'supplier' and self.payment_type == 'outbound':
            self.other_destination_account_id = self.partner_id.property_account_payable_id.id

        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_(
                    'There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
            self.other_destination_account_id = self.company_id.transfer_account_id.id
        # elif self.partner_id:
        #     if self.partner_type == 'customer':
        #         self.other_destination_account_id = self.partner_id.property_account_receivable_id.id
        #     else:
        #         self.other_destination_account_id = self.partner_id.property_account_payable_id.id
        elif self.partner_type == 'customer':
            default_account = self.env['ir.property']._get('property_account_receivable_id', 'res.partner')
            if default_account:
                self.other_destination_account_id = default_account.id
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property']._get('property_account_payable_id', 'res.partner')
            if default_account:
                self.other_destination_account_id = default_account.id
        if self.type_of_check == 'utility':
            self.other_destination_account_id = self.journal_id.utility_account_receivable_id.id

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_for_des(self):
            if self.analytic_account_id:
                self.other_destination_account_id = self.analytic_account_id.property_account_receivable_id.id


    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one outstanding payments/receipts account.",
                        move.display_name,
                    ))

                # if len(counterpart_lines) != 1:
                #     raise UserError(_(
                #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #         "include one and only one receivable/payable account (with an exception of "
                #         "internal transfers).",
                #         move.display_name,
                #     ))

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, "
                        "all optional journal items must share the same account.",
                        move.display_name,
                    ))

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same currency.",
                        move.display_name,
                    ))

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same partner.",
                        move.display_name,
                    ))

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))


