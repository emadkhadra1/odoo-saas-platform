# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta


class AccountPaymentInherited(models.Model):
    _inherit = "account.payment"

    # @api.onchange('partner_id')
    # def _get_partner_offers(self):
    #     lst = [offer.id for offer in self.env['sale.order'].search([('partner_id','=',self.partner_id.id)])]
    #     return {'domain': {'offer_id': [('id','in',lst)]}}

    @api.model
    def create(self, vals):
        res = super(AccountPaymentInherited, self).create(vals)
        if res.analytic_account_id:
            res.move_id.line_ids.write({'analytic_account_id': res.analytic_account_id.id})
        return res


    def action_post(self):
        super(AccountPaymentInherited, self).action_post()
        for rec in self:
            if rec.so_id and rec.unit_id:
                payments = sum(self.env['account.move'].search([]).filtered(lambda x: x.sale_order == rec.so_id and x.unit_id == rec.unit_id and x.pay_type == 'contracting').mapped('amount_total_signed'))
                contracting_amount = sum(
                    rec.so_id.order_line.filtered(lambda x: x.pay_type == 'contracting').mapped('price_subtotal'))
            else:
                pass
            if rec.pay_type == 'reservation':
                rec.unit_id.action_book_product()
                if self.so_id:
                    if self.so_id.opportunity_id:
                        rec.so_id.opportunity_id.stage_id = self.env.ref('real_estate_crm.stage_reserved').id

    # @api.onchange('offer_id')
    # def get_hold_amount(self):
    #     self.amount = self.offer_id.hold_amount

    batch_name = fields.Char('Name')
    so_id = fields.Many2one('sale.order', string='Sale Order')
    offer_id = fields.Many2one('sale.order', string='Offer')
    unit_id = fields.Many2one('product.template', compute="compute_unit_id")
    unit_state = fields.Selection(related="unit_id.state")
    cheque_no = fields.Char(string="Cheque No.", required=False, )
    notes = fields.Text(string="Notes", required=False, )
    install_id = fields.Many2one(comodel_name="account.move", string='Installment')

    def compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.so_id.unit_id.id or rec.offer_id.unit_id.id or False
            # if rec.so_id:
            #     rec.unit_id = rec.so_id.id
            # elif rec.offer_id:
            #     rec.unit_id = rec.offer_id.unit_id.id
            # else:
            #     rec.unit_id = False


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_blank = fields.Boolean(string="Blank Journal")


class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")

    @api.depends('can_edit_wizard', 'company_id')
    def _compute_journal_id(self):
        for wizard in self:
            # if wizard.can_edit_wizard:
            #     batch = wizard._get_batches()[0]
            #     wizard.journal_id = wizard._get_batch_journal(batch)
            # else:
            wizard.journal_id = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
                ('is_blank', '=', True),
            ], limit=1)
