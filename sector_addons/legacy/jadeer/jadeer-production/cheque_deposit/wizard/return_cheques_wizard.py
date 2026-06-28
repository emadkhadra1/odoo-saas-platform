from odoo import api, fields, models,_
from odoo.exceptions import UserError


class ReturnChequeDate(models.TransientModel):
    _name = 'return.cheque.date'

    payment_id = fields.Many2one(comodel_name="account.payment",)
    date = fields.Date(string="", required=False, )
    check_ty = fields.Selection([('check','شيك قضايا'),('check2', 'شيك أمانات')],
                                     string='Check')

    def action_check_returned(self):
            if self.payment_id.payment_status in ['deposit','posted'] or self.payment_id.payment_status == 'selfycle':
                if self.payment_id.payment_type == 'inbound':
                    journal = self.payment_id.check_deposit_id.bank_journal_id.id
                    if self.payment_id.check_deposit_id.bank_journal_id.return_debit_check_account_id:
                        debit_return_account = self.payment_id.check_deposit_id.bank_journal_id.return_debit_check_account_id.id
                    else:
                        raise UserError(_("Missing Return Check Debit Account on bank journal"))
                    if self.payment_id.check_deposit_id.bank_journal_id.credit_check_account_id:
                        credit_check_account = self.payment_id.check_deposit_id.bank_journal_id.credit_check_account_id.id
                    else:
                        raise UserError(_("Missing Credit Check Account on bank journal"))
                if self.payment_id.payment_type == 'outbound':
                    journal = self.payment_id.journal_id.id
                    if self.payment_id.journal_id.issue_return_account_id:
                        debit_return_account = self.payment_id.journal_id.issue_return_account_id.id
                    else:
                        raise UserError(_("Missing Return Check return Account on journal"))
                    if self.payment_id.partner_id.property_account_payable_id:
                        credit_check_account = self.payment_id.partner_id.property_account_payable_id.id
                    else:
                        raise UserError(_("Missing Payable Check Account on  Partner"))
                move_id = self.env['account.move'].create({
                    'ref': str(self.payment_id.check_deposit_id.name),
                    'journal_id':journal,
                    'date': self.date
                })
                debit_side = {
                    'name': "Return " + (str(self.payment_id.check_deposit_id.name) if self.payment_id.check_deposit_id else str(self.payment_id.name)),
                    'account_id': debit_return_account,
                    'debit': self.payment_id.amount,
                    'move_id': move_id.id,
                    # 'returned_items_id': self.id,
                    # 'move_state': 'returned',
                    'payment_id': self.payment_id.id,
                    'partner_id': self.payment_id.partner_id.id,
                    }
                credit_side = {
                        'name': "Return " + (str(self.payment_id.check_deposit_id.name) if self.payment_id.check_deposit_id else str(self.payment_id.name)),
                        'account_id': credit_check_account,
                        'credit': self.payment_id.amount,
                        # 'returned_items_id': self.id,
                        # 'move_state': 'returned',
                        'payment_id': self.payment_id.id,
                        'move_id': move_id.id,
                        'partner_id': self.payment_id.partner_id.id,
                    }

                move_id.sudo().write({'line_ids': [(0, 0,debit_side),(0, 0,credit_side)]})

                move_id.action_post()
                self.payment_id.payment_status = 'returned'
                self.payment_id.check_ty = self.check_ty
                # self.payment_id.checks_return_date = self.date
                # line.select = False

