from odoo import api, fields, models,_
from odoo.exceptions import UserError


class ReturnChequeToPartnerDate(models.TransientModel):
    _name = 'return.cheque.partner.date'

    payment_id = fields.Many2one(comodel_name="account.payment",)
    date = fields.Date(string="", required=False, )
    


    def action_check_returned_to_partner(self):
            if self.payment_id.payment_status == 'bounced'or self.payment_id.payment_status == 'posted':
                if self.payment_id.journal_id.default_account_id:
                    credit_return_account = self.payment_id.journal_id.default_account_id.id
                else:
                    raise UserError(_("Missing Return Check Debit Account on bank journal"))

                if self.payment_id.other_destination_account_id:
                    debit_check_account = self.payment_id.other_destination_account_id.id
                else:
                    raise UserError(_("Missing Destination Check Account on Payment"))

                move_id = self.env['account.move'].create({
                    'ref': str(self.payment_id.check_deposit_id.name),
                    'journal_id': self.payment_id.check_deposit_id.bank_journal_id.id,
                    'date': self.date
                })

                sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': "Return " + str(self.payment_id.check_deposit_id.name),
                    'account_id': credit_return_account,
                    'credit': self.payment_id.amount,
                    'move_id': move_id.id,
                    'payment_id': self.payment_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': "Return " + str(self.payment_id.check_deposit_id.name),
                    'account_id': debit_check_account,
                    'debit': self.payment_id.amount,
                    'payment_id': self.payment_id.id,
                    'move_id': move_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                })
                move_id.action_post()
                self.payment_id.payment_status = 'closed'

class ReturnChequeToPayDate(models.TransientModel):
    _name = 'return.cheque.pay.date'

    payment_id = fields.Many2one(comodel_name="account.payment",)
    date = fields.Date(string="", required=False, )



    def action_check_returned_to_partner(self):
            if self.payment_id.payment_status == 'returned':
                if self.payment_id.journal_id.default_account_id:
                    credit_return_account = self.payment_id.journal_id.default_account_id.id
                else:
                    raise UserError(_("Missing Return Check Debit Account on bank journal"))

                if self.payment_id.other_destination_account_id:
                    debit_check_account = self.payment_id.other_destination_account_id.id
                else:
                    raise UserError(_("Missing Destination Check Account on Payment"))
                move_id = self.env['account.move'].create({
                    'ref': str(self.payment_id.check_deposit_id.name),
                    'journal_id': self.payment_id.journal_id.id,
                    'date': self.date
                })
                sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
                sale_move_lines |= sale_move_lines.create({
                    'name': "Return To Customer" + str(self.payment_id.check_deposit_id.name),
                    'account_id': credit_return_account,
                    'credit': self.payment_id.amount,
                    'move_id': move_id.id,
                    'payment_id': self.payment_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                })
                sale_move_lines |= sale_move_lines.create({
                    'name': "Return To Customer " + str(self.payment_id.check_deposit_id.name),
                    'account_id': debit_check_account,
                    'debit': self.payment_id.amount,
                    'payment_id': self.payment_id.id,
                    'move_id': move_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                })
                move_id.action_post()
                self.payment_id.payment_status = 'returned_to_customer'


