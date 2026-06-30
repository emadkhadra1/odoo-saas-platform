# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from lxml import etree
import json

to_19_ar = (u'Ã˜ÂµÃ™ÂÃ˜Â±', u'Ã™Ë†Ã˜Â§Ã˜Â­Ã˜Â¯', u'Ã˜Â§Ã˜Â«Ã™â€ Ã˜Â§Ã™â€ ', u'Ã˜Â«Ã™â€žÃ˜Â§Ã˜Â«Ã˜Â©', u'Ã˜Â£Ã˜Â±Ã˜Â¨Ã˜Â¹Ã˜Â©', u'Ã˜Â®Ã™â€¦Ã˜Â³Ã˜Â©', u'Ã˜Â³Ã˜ÂªÃ˜Â©',
            u'Ã˜Â³Ã˜Â¨Ã˜Â¹Ã˜Â©', u'Ã˜Â«Ã™â€¦Ã˜Â§Ã™â€ Ã™Å Ã˜Â©', u'Ã˜ÂªÃ˜Â³Ã˜Â¹Ã˜Â©', u'Ã˜Â¹Ã˜Â´Ã˜Â±Ã˜Â©', u'Ã˜Â£Ã˜Â­Ã˜Â¯ Ã˜Â¹Ã˜Â´Ã˜Â±', u'Ã˜Â§Ã˜Â«Ã™â€ Ã˜Â§ Ã˜Â¹Ã˜Â´Ã˜Â±', u'Ã˜Â«Ã™â€žÃ˜Â§Ã˜Â«Ã˜Â© Ã˜Â¹Ã˜Â´Ã˜Â±',
            u'Ã˜Â£Ã˜Â±Ã˜Â¨Ã˜Â¹Ã˜Â© Ã˜Â¹Ã˜Â´Ã˜Â±Ã˜Â©', u'Ã˜Â®Ã™â€¦Ã˜Â³Ã˜Â© Ã˜Â¹Ã˜Â´Ã˜Â±', u'Ã˜Â³Ã˜Âª Ã˜Â¹Ã˜Â´Ã˜Â±Ã˜Â©', u'Ã˜Â³Ã˜Â¨Ã˜Â¹Ã˜Â© Ã˜Â¹Ã˜Â´Ã˜Â±', u'Ã˜Â«Ã™â€¦Ã˜Â§Ã™â€ Ã™Å Ã˜Â© Ã˜Â¹Ã˜Â´Ã˜Â±', u'Ã˜ÂªÃ˜Â³Ã˜Â¹Ã˜Â© Ã˜Â¹Ã˜Â´Ã˜Â±')

tens_ar = (u'', u'', u'Ã˜Â¹Ã˜Â´Ã˜Â±Ã™Ë†Ã™â€ ', u'Ã˜Â«Ã™â€žÃ˜Â§Ã˜Â«Ã™Ë†Ã™â€ ', u'Ã˜Â£Ã˜Â±Ã˜Â¨Ã˜Â¹Ã™Ë†Ã™â€ ', u'Ã˜Â®Ã™â€¦Ã˜Â³Ã™Ë†Ã™â€ ', u'Ã˜Â³Ã˜ÂªÃ™Ë†Ã™â€ ', u'Ã˜Â³Ã˜Â¨Ã˜Â¹Ã™Ë†Ã™â€ ', u'Ã˜Â«Ã™â€¦Ã˜Â§Ã™â€ Ã™Ë†Ã™â€ ', u'Ã˜ÂªÃ˜Â³Ã˜Â¹Ã™Ë†Ã™â€ ')

hund_ar = (u'', u'', u'Ã™â€¦Ã˜Â¦Ã˜ÂªÃ˜Â§Ã™â€ ', u'Ã˜Â«Ã™â€žÃ˜Â§Ã˜Â«Ã™â€¦Ã˜Â§Ã˜Â¦Ã˜Â©', u'Ã˜Â§Ã˜Â±Ã˜Â¨Ã˜Â¹Ã™â€¦Ã˜Â§Ã˜Â¦Ã˜Â©', u'Ã˜Â®Ã™â€¦Ã˜Â³Ã™â€¦Ã˜Â§Ã˜Â¦Ã˜Â©', u'Ã˜Â³Ã˜ÂªÃ™â€¦Ã˜Â§Ã˜Â¦Ã˜Â©', u'Ã˜Â³Ã˜Â¨Ã˜Â¹Ã™â€¦Ã˜Â§Ã˜Â¦Ã˜Â©',
           u'Ã˜Â«Ã™â€¦Ã˜Â§Ã™â€ Ã™â€¦Ã˜Â¦Ã˜Â©', u'Ã˜ÂªÃ˜Â³Ã˜Â¹Ã™â€¦Ã˜Â§Ã˜Â¦Ã˜Â©')


def convert_less_100(number):
    if number <= 19:
        number = int(number)
        return to_19_ar[number]
    elif number < 100:
        ten = number / 10
        rest = number % 10
        if rest != 0:
            rest = int(rest)
            ten = int(ten)
            return to_19_ar[rest] + u' Ã™Ë† ' + tens_ar[ten]
        else:
            rest = int(rest)
            ten = int(ten)
            return tens_ar[ten]


def convert_less_1000(number):
    hund = number / 100
    rest = number % 100
    rest = int(rest)
    hund = int(hund)

    if hund == 0:
        hund_text = u''
    elif hund == 1:
        hund_text = u'Ã™â€¦Ã˜Â¦Ã˜Â©'
    elif hund < 10:
        hund_text = hund_ar[hund]
    else:
        hund_text = convert_less_1000(hund) + u' Ã™â€¦Ã˜Â¦Ã˜Â© '
    if rest != 0:
        if hund_text != u'':
            hund_text = hund_text + u' Ã™Ë† ' + convert_to_ar(rest)
        else:
            hund_text = convert_to_ar(rest)
    return hund_text


def convert_less_10000(number):
    thous = number / 1000
    rest = number % 1000
    if thous == 0:
        thous_text = u''
    elif thous == 1:
        thous_text = u'Ã˜Â§Ã™â€žÃ™Â'
    elif thous == 2:
        thous_text = u'Ã˜Â§Ã™â€žÃ™ÂÃ˜Â§Ã™â€ '
    elif thous <= 10:
        thous_text = convert_less_100(thous) + u'Ã˜Â¢Ã™â€žÃ˜Â§Ã™Â'
    else:
        thous_text = convert_less_1000(thous) + u' Ã˜Â§Ã™â€žÃ™Â '
    if rest != 0:
        if thous_text != u'':
            thous_text = thous_text + u' Ã™Ë† ' + convert_to_ar(rest)
        else:
            thous_text = convert_to_ar(rest)
    return thous_text


def convert_less_billion(number):
    million = number / 1000000
    rest = number % 1000000
    if million == 1:
        million_text = u'Ã™â€¦Ã™â€žÃ™Å Ã™Ë†Ã™â€ '
    elif million == 2:
        million_text = u'Ã™â€¦Ã™â€žÃ™Å Ã™Ë†Ã™â€ Ã™Å Ã™â€ '
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'Ã™â€¦Ã™â€žÃ˜Â§Ã™Å Ã™Å Ã™â€ '
    else:
        million_text = convert_less_1000(million) + u' ' + u'Ã™â€¦Ã™â€žÃ™Å Ã™Ë†Ã™â€ '
    if rest != 0:
        million_text = million_text + u' Ã™Ë† ' + convert_to_ar(rest)
    return million_text


def convert_over_billion(number):
    million = number / 1000000000
    rest = number % 1000000000
    if million == 1:
        million_text = u'Ã™â€¦Ã™â€žÃ™Å Ã˜Â§Ã˜Â±'
    elif million == 2:
        million_text = u'Ã™â€¦Ã™â€žÃ™Å Ã˜Â§Ã˜Â±Ã™Å Ã™â€ '
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'Ã™â€¦Ã™â€žÃ™Å Ã˜Â§Ã˜Â±Ã˜Â§Ã˜Âª'
    else:
        million_text = convert_less_1000(million) + u' ' + u'Ã™â€¦Ã™â€žÃ™Å Ã˜Â§Ã˜Â±'
    if rest != 0:
        million_text = million_text + u' Ã™Ë† ' + convert_to_ar(rest)
    return million_text


def convert_to_ar(number):
    if number < 100:
        return convert_less_100(number)
    elif number < 1000 and number >= 100:
        return convert_less_1000(number)
    elif number < 1000000 and number >= 1000:
        return convert_less_10000(number)
    elif number < 1000000000 and number >= 1000000:
        return convert_less_billion(number)
    else:
        return convert_over_billion(number)


def amount_to_text_ar(number, currency):
    list = str(number).split('.')
    start_word = convert_to_ar(abs(int(list[0])))

    if start_word == u'Ã™Ë†Ã˜Â§Ã˜Â­Ã˜Â¯':
        currenc = u'Ã˜Â¬Ã™â€ Ã™Å Ã™â€¡Ã˜Â§'
    elif start_word in [u'Ã˜Â«Ã™â€žÃ˜Â§Ã˜Â«Ã˜Â©', u'Ã˜Â£Ã˜Â±Ã˜Â¨Ã˜Â¹Ã˜Â©', u'Ã˜Â®Ã™â€¦Ã˜Â³Ã˜Â©', u'Ã˜Â³Ã˜ÂªÃ˜Â©',
                        u'Ã˜Â³Ã˜Â¨Ã˜Â¹Ã˜Â©', u'Ã˜Â«Ã™â€¦Ã˜Â§Ã™â€ Ã™Å Ã˜Â©', u'Ã˜ÂªÃ˜Â³Ã˜Â¹Ã˜Â©', u'Ã˜Â¹Ã˜Â´Ã˜Â±Ã˜Â©']:
        currenc = u'Ã˜Â¬Ã™â€ Ã™Å Ã™â€¡Ã˜Â§Ã˜Âª'
    else:
        currenc = u'Ã˜Â¬Ã™â€ Ã™Å Ã™â€¡Ã˜Â§'
    end_word = convert_to_ar(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and u' Ã™â€šÃ˜Â±Ã˜Â´Ã˜Â§ ' or u' Ã™â€šÃ˜Â±Ã˜Â´Ã˜Â§ '
    final_result = start_word + u' ' + currenc + u' Ã™Ë† ' + end_word + u' ' + cents_name
    return final_result


if __name__ == '__main__':
    number = 23539000002.50
    currency = u' Ã˜Â¬Ã™â€ Ã™Å Ã˜Â© Ã™â€¦Ã˜ÂµÃ˜Â±Ã™Å  '


def amount_to_text_ar_area(number):
    list = str(number).split('.')
    if list:
        start_word = convert_to_ar(abs(int(list[0])))

        if start_word == u'Ã™Ë†Ã˜Â§Ã˜Â­Ã˜Â¯':
            currenc = u'Ã™â€¦Ã˜ÂªÃ˜Â±Ã˜Â§'
        elif start_word in [u'Ã˜Â«Ã™â€žÃ˜Â§Ã˜Â«Ã˜Â©', u'Ã˜Â£Ã˜Â±Ã˜Â¨Ã˜Â¹Ã˜Â©', u'Ã˜Â®Ã™â€¦Ã˜Â³Ã˜Â©', u'Ã˜Â³Ã˜ÂªÃ˜Â©',
                            u'Ã˜Â³Ã˜Â¨Ã˜Â¹Ã˜Â©', u'Ã˜Â«Ã™â€¦Ã˜Â§Ã™â€ Ã™Å Ã˜Â©', u'Ã˜ÂªÃ˜Â³Ã˜Â¹Ã˜Â©', u'Ã˜Â¹Ã˜Â´Ã˜Â±Ã˜Â©']:
            currenc = u'Ã˜Â§Ã™â€¦Ã˜ÂªÃ˜Â§Ã˜Â±'
        else:
            currenc = u'Ã˜Â§Ã™â€¦Ã˜ÂªÃ˜Â§Ã˜Â±'
        end_word = convert_to_ar(int(list[1]))
        final_result = start_word + u' ' + currenc
        return final_result


if __name__ == '__main__':
    number = 23539000002.50
    currency = u' Ã˜Â¬Ã™â€ Ã™Å Ã˜Â© Ã™â€¦Ã˜ÂµÃ˜Â±Ã™Å  '


class SaleOrderInherited(models.Model):
    _inherit = "sale.order"

    invoice_inv = fields.Boolean(default=False, copy=False)
    partner_set = fields.Boolean(default=False, copy=False)
    check = fields.Boolean(default=False, copy=False)
    readonly = fields.Boolean(default=False, copy=False)
    repeat_installements = fields.Boolean(default=False, copy=False)
    inv_calc_payment = fields.Boolean(default=False, copy=False)
    reserve = fields.Boolean(default=False, copy=False)
    request_hold = fields.Boolean(default=False, copy=False)
    request_reserve = fields.Boolean(default=False, copy=False)
    hold_amount = fields.Float(string="Reservation Amount")
    # hold_close_date = fields.Datetime()
    discount_request_id = fields.Many2one(comodel_name="discount.request")
    discount_amount = fields.Float(related="discount_request_id.discount_amount")
    payment_plan_id = fields.Many2one('payment.plan', string='Payment Plan')
    unit_payment_plan_id = fields.Many2many('payment.plan',compute='get_unit_payment_plan_id')
    last_invoice = fields.Many2one('account.move', compute='_compute_last_invoice')
    unit_id = fields.Many2one('product.template', string='Unit', required=False,
                              domain="[('is_residential', '=',True),('state', '=', 'sale'),]", )
    unit_state = fields.Selection(related='unit_id.state')
    state = fields.Selection([
        ('draft', 'Offer'),
        ('sent', 'Offer Sent'),
        # ('request_hold', 'Hold Request'),
        # ('sales_hold_approve', 'Sales Hold Approve'),
        # ('hold', 'Hold'),
        ('request_reserve', 'Reserve Request'),
        ('sales_reserve_approve', 'Sales Reserve Approve'),
        ('reservation', 'Reservation'),
        ('down_payment', 'DownPayment'),
        ('sale', 'Sale'),
        ('done', 'Locked'),
        ('cancel_request', 'Cancel Request'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=False, copy=False, index=True, track_visibility='onchange', default='draft')
    last_offer_state = fields.Selection([
        ('draft', 'Offer'),
        ('sent', 'Offer Sent'),
        # ('request_hold', 'Hold Request'),
        # ('sales_hold_approve', 'Sales Hold Approve'),
        # ('hold', 'Hold'),
        ('request_reserve', 'Reserve Request'),
        ('sales_reserve_approve', 'Sales Reserve Approve'),
        ('reservation', 'Reservation'),
        ('down_payment', 'DownPayment'),
        ('sale', 'Sale'),
        ('done', 'Locked'),
        ('cancel_request', 'Cancel Request'),
        ('cancel', 'Cancelled'),
    ], string='Last Offer Status', readonly=False, copy=False, index=True, default='draft',compute='get_last_offer_status',store=True)
    @api.depends('state')
    def get_last_offer_status(self):
        for rec in self:
            if rec.state in ['draft','sent','request_reserve','sales_reserve_approve','reservation','down_payment','sale','done',]:
                rec.last_offer_state = rec.state

    total_amount = fields.Float(related="unit_id.list_price",string="Total Amount")
    unit_price = fields.Float(compute='_compute_unit_price',string="Unit Price")
    total_attached_area = fields.Float(related="unit_id.total_attached_area",string="Attached Area")
    total_utilities = fields.Float(related="unit_id.total_utilities",string="Utilities")
    min_deposit_amount = fields.Monetary(related='unit_id.min_deposit_amount_temp')
    arabic_amount = fields.Char(compute='_compute_arabic_amount', default='')
    arabic_amount_unit = fields.Char(compute='_compute_arabic_amount_unit', default='')
    remain_arabic_amount = fields.Char(compute='_compute_remain_arabic_amount', default='')
    arabic_area = fields.Char(compute='_compute_arabic_area', default='')
    installment_count = fields.Integer(string="Installments", compute="calc_installment_count")
    broker_id = fields.Many2one('res.partner', string="Broker")
    broker_manager_id = fields.Many2one('res.partner',string="Broker manager")
    broker_sales_id = fields.Many2one('res.partner',string="Broker Sales")
    local_overseas = fields.Selection(string="Local/Overseas", selection=[('local', 'Local'),
                                                                          ('overseas', 'Overseas'), ], required=False, )
    source = fields.Selection(string="Source", selection=[('direct', 'Direct'),
                                                          ('indirect', 'Indirect'),('personal','Personal'),('ambassador','Ambassador'), ], required=False,)
    reservation_date = fields.Datetime(string="Reservation Date")
    contract_date = fields.Date(string="Contract Date")
    unreserve_date = fields.Datetime(string="Unreserve Date",compute="compute_unreserve_date",store=True)
    utility_amount = fields.Monetary(compute="compute_utility_amount")
    subtotal_amount = fields.Monetary(compute="compute_subtotal_amount")
    reservation_percentage = fields.Float(compute="compute_reservation_amount", digits=0)
    reservation_amount = fields.Monetary(compute="compute_reservation_amount")
    sale_person2_id = fields.Many2one(comodel_name="res.users", string="Salesperson 2", required=False, )
    sale_person3_id = fields.Many2one(comodel_name="res.users", string="Salesperson 3", required=False, )


    @api.constrains('unit_id.list_price','subtotal_amount','order_line','order_line.unit_price')
    def get_unit_total_amount(self):
            if self.subtotal_amount > self.unit_id.list_price:
                raise ValidationError('Unit Price Amount Cant be greater than Unit Price Amount')
    # @api.depends('order_line','order_line.pay_type')
    def compute_reservation_amount(self):
        for rec in self:
            reservation_amount = 0
            reservation_percentage = 0
            if rec.order_line:
               reservation_amount = sum(rec.order_line.filtered(lambda x: x.pay_type == 'reservation').mapped('price_subtotal'))
               reservation_percentage = int(sum(rec.order_line.filtered(lambda x: x.pay_type == 'reservation').mapped('percentage')))
            else:
                pass
            rec.reservation_percentage = reservation_percentage
            rec.reservation_amount = reservation_amount
            # @api.depends('order_line','order_line.product_utility_ids')
    def compute_subtotal_amount(self):
        for rec in self:
            subtotal_amount = 0
            if rec.order_line:
               subtotal_amount = sum(rec.order_line.filtered(lambda x: not x.product_utility_ids).mapped('price_subtotal'))
            else:
                pass
            rec.subtotal_amount =subtotal_amount
    # @api.depends('order_line','order_line.product_utility_ids')
    def compute_utility_amount(self):
        for rec in self:
            utility_amount = 0
            if rec.order_line:
               utility_amount = sum(rec.order_line.filtered(lambda x: x.product_utility_ids).mapped('price_subtotal'))
            else:
                pass
            rec.utility_amount = utility_amount
    @api.depends('unit_id')
    def _compute_unit_price(self):
        for rec in self:
            rec.unit_price = rec.unit_id.list_price - rec.unit_id.total_attached_area

    @api.depends('reservation_date','unit_id.reserve_days_no')
    def compute_unreserve_date(self):
        for rec in self:
            if rec.reservation_date and rec.unit_id.reserve_days_no:
                rec.unreserve_date = rec.reservation_date + relativedelta(days=rec.unit_id.reserve_days_no)
            else:
                rec.unreserve_date = False

    @api.onchange('opportunity_id')
    @api.constrains('opportunity_id')
    def onchange_lead(self):
        for rec in self:
            rec.broker_id = rec.opportunity_id.broker_id.id
            rec.local_overseas = rec.opportunity_id.local_overseas
            rec.source = rec.opportunity_id.source

    @api.depends('order_line', 'order_line.install_inv_id')
    def calc_installment_count(self):
        for order in self:
            invoices = self.env['account.move'].sudo().search([
                ('partner_id', '=', order.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('sale_order', '=', order.id),
            ])
            order.installment_count = len(invoices)

    def action_cancel(self):
        for record in self:
            if record.unit_id:
                record.unit_id.state = 'sale'
                record.unit_id.customer_id = False

        return self.write({'state': 'cancel'})

    @api.depends('unit_id')
    def _compute_arabic_amount_unit(self):
        for line in self:
            line.arabic_amount_unit = amount_to_text_ar(line.unit_id.list_price, line.currency_id.symbol)

    @api.depends('last_invoice', 'unit_id')
    def _compute_remain_arabic_amount(self):
        for line in self:
            line.remain_arabic_amount = amount_to_text_ar(line.amount_total - line.last_invoice.amount_total,
                                                          line.currency_id.symbol)

    @api.depends('last_invoice', 'unit_id')
    def _compute_arabic_amount(self):
        for line in self:
            line.arabic_amount = amount_to_text_ar(line.last_invoice.amount_total, line.currency_id.symbol)

    def action_create_checks(self):
        return {
            'name': "Offer",
            'context': {
                'default_unit_id': self.unit_id.id,
                'default_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount_total,
            },
            'view_mode': 'form',
            'res_model': 'account.batch.payment',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_request_reserve(self):
        if self.discount_request_id and self.discount_request_id.state not in ['approved', 'rejected']:
            raise ValidationError("Sorry, There is a Discount Request Need to Approved")
        return {
            'name': "Request Reserve",
            'view_mode': 'form',
            'res_model': 'reserve.request.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_unit_id': self.unit_id.id,
                'default_offer_id': self.id,
            },
        }

    def action_request_discount(self):
        return {
            'name': "Request Discount",
            'view_mode': 'form',
            'res_model': 'discount.request.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_unit_id': self.unit_id.id,
                'default_offer_id': self.id,
            },
        }

    @api.depends('unit_id')
    def _compute_arabic_area(self):
        for line in self:
            line.arabic_area = amount_to_text_ar_area(line.unit_id.total_Area)

    @api.depends('unit_id', 'partner_id')
    def _compute_last_invoice(self):
        for line in self:
            line.last_invoice = False
            invoice_ids = self.env['account.move'].search(
                [('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), ('payment_state', '=', 'paid'),
                 ('unit_id', '=', self.unit_id.id),
                 ('partner_id', '=', self.partner_id.id)], limit=1)
            if invoice_ids:
                line.last_invoice = invoice_ids[0]

    @api.constrains('unit_id', 'unit_id.customer_id', 'partner_id', 'unit_id.state')
    def check_partner_of_unit_id(self):
        for line in self:
            if line.unit_id:
                if line.unit_id.state != 'sale':
                    pass
                    # raise ValidationError("Sorry, This Unit not for sale")
                if line.unit_id.customer_id and line.partner_id:
                    if line.unit_id.customer_id != line.partner_id:
                        raise ValidationError(
                            "Sorry, This Unit reserved before to  " + str(line.unit_id.customer_id.name))

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        for line in self:
            if line.unit_id:
                if line.unit_id.customer_id:
                    # line.partner_set = True
                    line.partner_id = line.unit_id.customer_id
                # else:
                #     line.partner_set = False

    def action_create_installement(self):
        self.action_create_sale_installement()

    def action_create_sale_installement(self):
        for line in self:
            line.invoice_inv = True
        if not self.unit_id.project_id:
            raise exceptions.ValidationError('You should define project on this unit')
        else:
            if not self.unit_id.project_id.property_account_receivable_id:
                raise exceptions.ValidationError('You should define Receivable Account on unit Project')

        if self.order_line:
            for line in self.order_line:
                if line.recerv_unit == False and line .pay_type != 'contracting':
                    if line.pay_type == 'contracting':
                        pay_type = 'Ã˜Â¯Ã™ÂÃ˜Â¹Ã™â€¡ Ã˜ÂªÃ˜Â¹Ã˜Â§Ã™â€šÃ˜Â¯'
                    if line.pay_type == 'delivery':
                        pay_type = 'Ã˜Â¯Ã™ÂÃ˜Â¹Ã™â€¡ Ã˜ÂªÃ™Ë†Ã˜ÂµÃ™Å Ã™â€ž'
                    if line.pay_type == 'installment':
                        pay_type = 'Ã™â€šÃ˜Â³Ã˜Â·'
                    if line.pay_type == 'reservation':
                        pay_type = 'Ã˜Â¯Ã™ÂÃ˜Â¹Ã˜Â© Ã˜Â­Ã˜Â¬Ã˜Â²'
                    if line.pay_type == 'maintenance':
                        pay_type = 'Ã˜Â¯Ã™ÂÃ˜Â¹Ã˜Â© Ã˜ÂµÃ™Å Ã˜Â§Ã™â€ Ã˜Â©'
                    invoice_vals = {
                        'sale_order': self.id,
                        'unit_id': self.unit_id.id,
                        'partner_id': self.partner_id.id,
                        'invoice_date_due': line.start_date,
                        'invoice_date': self.contract_date,
                        'analytic_account_id': self.unit_id.analytic_account_id.id,
                        'move_type': 'out_invoice',
                        'state': 'draft',
                        'pay_type': line.pay_type,
                        'invoice_payment_term_id': False,
                    }
                    account_id = ""
                    ref = self.name + ' / ' + self.partner_id.name + ' / ' + pay_type
                    if line.product_utility_ids:
                        account_id = line.product_utility_ids.name.account_id.id
                        #from elbatal 10/10/2021

                        journal_id = line.product_utility_ids.name.journal_id.id
                        receivable_account_id = line.product_utility_ids.name.receivable_account_id.id
                        invoice_vals.update({'journal_id': journal_id,'ref':line.product_utility_ids.name.name,
                                             'utility_invoice':True})
                        ref = line.product_utility_ids.name.name + '/' + self.name + ' / ' + self.partner_id.name + ' / ' + pay_type
                        if not account_id:
                            raise UserError(
                                _(
                                    ' There is no  account defined for this Utility: "%s".') %
                                (line.product_utility_ids.name.name))
                        if not receivable_account_id:
                            raise UserError(
                                _(
                                    ' There is no  Receivable account defined for this Utility: "%s".') %
                                (line.product_utility_ids.name.name))
                        if not journal_id:
                            raise UserError(
                                _(
                                    ' There is no  Journal defined for this Utility: "%s".') %
                                (line.product_utility_ids.name.name))
                    else:
                        if line.product_id:
                            account_id = line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id
                        if not account_id:
                            raise UserError(
                                _(
                                    'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                                (line.product_id.product_tmpl_id.name,))
                    product_default = self.env['ir.model.data'].search_read(
                        [('model', '=', 'product.product'), ('name', '=', 'product_product_19_bom')])
                    xx = line.price_unit - line.amount_percentage
                    invoice_line_ids = []
                    invoice_line_ids.append((0, 0, {
                        'name': ref,
                        'account_id': account_id,
                        'product_id': line.product_id.id,
                        'quantity': 1,
                        'analytic_account_id': self.unit_id.product_project.id,
                        'price_unit': line.price_unit - line.amount_percentage,
                        'utility_id': line.product_utility_ids.id
                    }))
                    if line.amount_percentage:
                        invoice_line_ids.append((0, 0, {
                            'name': self.name + ' / ' + self.partner_id.name + '/ Interest',
                            'account_id': account_id,
                            'product_id': product_default[0]['res_id'],
                            'quantity': 1,
                            'analytic_account_id': self.unit_id.product_project.id,
                            'price_unit': line.amount_percentage,
                        }))
                    invoice_vals.update({'invoice_line_ids': invoice_line_ids})
                    inv = self.env['account.move'].create(invoice_vals)
                    # from elbatal 10/10/2021

                    if line.product_utility_ids and receivable_account_id:
                        receivable = inv.line_ids.filtered(lambda x: x.debit > 0)
                        receivable.account_id = receivable_account_id
                    line.install_inv_id = inv
        else:
            pass
        self.check = True

    def action_reserve_unit(self):
        blank_journal = self.env['account.journal'].search([('type', 'in', ['bank', 'cash']),
                                                            ('company_id', '=', self.env.user.company_id.id),
                                                            ('is_blank', '=', True)], limit=1)
        self.env['account.payment'].create({
                'payment_type': 'inbound',
                'pay_type': 'reservation',
                'unit_id': self.unit_id.id,
                'partner_id': self.partner_id.id,
                'amount': self.hold_amount,
                'date': self.contract_date if self.contract_date else fields.datetime.now(),
                'journal_id': blank_journal.id if blank_journal else False,
                'so_id': self.id,
                'offer_id': self.id,
                'analytic_account_id': self.unit_id.analytic_account_id.id,
            })
        self.state = 'reservation'
        # self.unit_id.action_book_product()

        self.reservation_date = fields.datetime.now()
        # self.action_send_notification(self.user_id.id)
        # if self.sale_person2_id:
        #     self.action_send_notification(self.sale_person2_id.id)
        # if self.sale_person3_id:
        #     self.action_send_notification(self.sale_person3_id.id)

    def action_make_down_payment(self):
        for line in self:
            if not line.order_line:
                raise ValidationError('Must provide Sale line')
            if line.unit_id:
                # if line.unit_id.state != 'sale':
                #     raise ValidationError("Sorry, This Unit not for sale")
                if line.unit_id.customer_id and line.partner_id:
                    if line.unit_id.customer_id != line.partner_id:
                        raise ValidationError(
                            "Sorry, This Unit reserved before to  " + str(line.unit_id.customer_id.name))
                if line.discount_request_id and line.discount_request_id.state not in ['approved','rejected']:
                    raise ValidationError("Sorry, There is a Discount Request Need to Approved")
        for rec in self.order_line:
            if rec.pay_type == 'contracting':

                # self.unit_id.action_book_product()
                self.unit_id.analytic_account_id.partner_id = self.partner_id
                self.opportunity_id.with_context(offer=True).action_set_won()
                invoice_vals = {
                    'sale_order': self.id,
                    'unit_id': self.unit_id.id,
                    'sale_order_line': rec.id,
                    'partner_id': self.partner_id.id,
                    # 'account_id': self.partner_id.property_account_receivable_id.id,
                    'date_temp': self.date_order.date(),
                    'invoice_date': self.contract_date,
                    'move_type': 'out_invoice',
                    'pay_type': 'contracting',
                    'analytic_account_id': self.unit_id.product_project.id,
                    'state': 'draft',
                    # 'journal_id': self.journal_id.id,
                }
                if self.unit_id.id:
                    account_id = self.unit_id.property_account_income_id.id or self.unit_id.categ_id.property_account_income_categ_id.id
                if not account_id:
                    raise UserError(
                        _(
                            'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (self.unit_id.product_variant_id.name,))

                # if self.unit_id.min_deposit_amount == 0:
                #     raise UserError(('Please add Min Deposit Amount For Unit "%s"') % (self.unit_id.name))
                reservation_amount = self.unit_id.min_deposit_amount
                reservation_line = self.order_line.filtered(lambda x : x.pay_type == 'contracting')
                if reservation_line:
                    reservation_amount = rec.price_subtotal
                invoice_lines = []
                invoice_lines.append((0, 0, {
                    'name': self.name + ' / ' + self.partner_id.name + ' / ' + 'Ã˜Â¯Ã™ÂÃ˜Â¹Ã™â€¡ Ã˜Â­Ã˜Â¬Ã˜Â²',
                    'account_id': account_id,
                    'product_id': self.unit_id.product_variant_id.id,
                    'quantity': 1,
                    'price_unit': reservation_amount,
                    'price_subtotal': self.unit_id.min_deposit_amount,
                    'analytic_account_id': self.unit_id.product_project.id,
                }))
                invoice_vals.update({'invoice_line_ids': invoice_lines})
                invoice = self.env['account.move'].create(invoice_vals)
                rec.install_inv_id = invoice.id
                self.with_context(from_seserv='yes').reserve = True
                self.state = 'down_payment'
                self.unit_id.sudo().update({'customer_id': self.partner_id})

    discount_amount = fields.Float('Amount',compute='unit_disc_amount')
    price_before_discount = fields.Float('Price Before Discount',related='unit_id.price_before_discount')
    price_disc = fields.Float('Discount Amount',related='unit_id.price_disc')

    def unit_disc_amount(self):
        for rec in self:
            discount_amount = 0
            if rec.unit_id.apply_discount:
                if rec.unit_id.discount_type == 'amount':
                    discount_amount = rec.unit_id.discount_amount
                elif rec.unit_id.discount_type == 'percentage':
                    discount_amount = rec.unit_id.discount_percentage
            rec.discount_amount = discount_amount

    # def action_reserve_unit(self):
    #     for line in self:
    #         if line.unit_id:
    #             if line.unit_id.customer_id and line.partner_id:
    #                 if line.unit_id.customer_id != line.partner_id:
    #                     raise ValidationError(
    #                         "Sorry, This Unit reserved before to  " + str(line.unit_id.customer_id.name))
    #             if line.discount_request_id and line.discount_request_id.state not in ['approved','rejected']:
    #                 raise ValidationError("Sorry, There is a Discount Request Need to Approved")
    #     self.unit_id.analytic_account_id.partner_id = self.partner_id
    #     self.opportunity_id.with_context(offer=True).action_set_won()
    #     if self.unit_id.id:
    #         account_id = self.unit_id.property_account_income_id.id or self.unit_id.categ_id.property_account_income_categ_id.id
    #     if not account_id:
    #         raise UserError(
    #             _(
    #                 'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
    #             (self.unit_id.product_variant_id.name,))
    #
    #     if self.unit_id.min_deposit_amount == 0:
    #         raise UserError(('Please add Min Deposit Amount For Unit "%s"') % (self.unit_id.name))
    #     self.env['account.payment'].create({
    #         'payment_type': 'inbound',
    #         'pay_type': 'reservation',
    #         'unit_id': self.unit_id.id,
    #         'partner_id': self.partner_id.id,
    #         'amount': self.unit_id.min_deposit_amount,
    #         # 'journal_id': self.journal_id.id,
    #         'so_id': self.id,
    #         'offer_id': self.id,
    #         'analytic_account_id': self.unit_id.analytic_account_id.id,
    #     })
    #     if self.order_line:
    #         for line in self.order_line:
    #             if line.pay_type == 'contracting' and not line.product_utility_ids and line.recerv_unit == False:
    #                 amount_reservation_per = (self.unit_id.min_deposit_amount * 100) / self.total_amount
    #                 reserv_per = line.percentage - amount_reservation_per
    #                 line.with_context(don_not_check=True).unit_price = line.unit_price - self.unit_id.min_deposit_amount
    #                 remain_per = line.percentage - reserv_per
    #                 line.percentage = reserv_per
    #                 self.env['sale.order.line'].with_context(don_not_check=True).create({
    #                     'percentage': remain_per,
    #                     'name': str(self.unit_id.name) + '/ Reservation',
    #                     'is_expense': False,
    #                     'value': 1,
    #                     'product_id': self.unit_id.id,
    #                     'product_uom': self.unit_id.uom_id.id,
    #                     'product_uom_qty': 1,
    #                     'schedule_period': 'day',
    #                     'no_of_installements': 1,
    #                     'recerv_unit': True,
    #                     'display_type': 'default',
    #                     'qty_delivered_manual': line.unit_price,
    #                     # 'price_unit': self.unit_id.min_deposit_amount,
    #                     'unit_price': round(self.unit_id.min_deposit_amount, 4),
    #                     'stop_per': True,
    #                     'tax_id': False,
    #                     'start_date': fields.date.today(),
    #                     'order_id': self.id,
    #                     # 'install_inv_id': inv_id.id,
    #                 })
    #     self.with_context(from_seserv='yes').reserve = True
    #     self.state = 'reservation'
    #     self.reservation_date = fields.datetime.now()
    #     self.unit_id.sudo().update({'customer_id': self.partner_id})

    def calculate_payment_plan(self):
        self.calculate_sale_payment_plan()

    def calculate_sale_payment_plan(self):
        self.inv_calc_payment = True
        for line in self.order_line:
            if not line.start_date:
                raise ValidationError("Please Add Start Date In Sale Order Line")
        order_lines = []
        for line in self.order_line:
            line_amount, fraction = self.calc_line_amount_without_fraction(line.no_of_installements, line.unit_price)
            if line.recerv_unit == False:
                res = int(line.value)
                end_date = line.start_date
                for i in range(0, int(line.product_uom_qty)):
                    date_temp = line.start_date
                    if line.schedule_period == 'day':
                        end_date = date_temp + relativedelta(days=+(res * i))
                    elif line.schedule_period == 'month':
                        end_date = date_temp + relativedelta(months=+(res * i))
                    line_date = line.schedule_period
                    percentage_per_unit = line.percentage / line.no_of_installements
                    interest_per_unit = line.interset / line.no_of_installements
                    sale_line = ({
                        'percentage': percentage_per_unit,
                        'value': line.value,
                        'schedule_period': line.schedule_period,
                        'duration': line.duration,
                        'pay_type': line.pay_type,
                        'name': line.name,
                        'is_expense': False,
                        'interset': interest_per_unit,
                        'start_date': str(end_date),
                        'product_id': self.unit_id.id,
                        'product_uom': self.unit_id.uom_id.id,
                        'product_uom_qty': line.no_of_installements,
                        'product_utility_ids': line.product_utility_ids.id,
                        'no_of_installements': 1,
                        'display_type': 'default',
                        'amount_percentage': line.amount_percentage / line.no_of_installements,
                        'qty_delivered_manual': line_amount + fraction if (
                                                                                  i + 1) == line.product_uom_qty else line_amount,
                        'unit_price': line_amount + fraction if (i + 1) == line.product_uom_qty else line_amount,
                        'stop_per': True,
                        'tax_id': False,
                    })
                    order_lines.append((0, 0, sale_line))
        for oper in self.order_line:
            if oper.recerv_unit == True:
                sale_line1 = ({
                    'percentage': oper.percentage,
                    'value': oper.value,
                    'schedule_period': oper.schedule_period,
                    'duration': oper.duration,
                    'pay_type': oper.pay_type,
                    'name': oper.name,
                    'is_expense': False,
                    'start_date': oper.start_date,
                    'product_id': self.unit_id.id,
                    'product_uom': self.unit_id.uom_id.id,
                    'product_uom_qty': oper.no_of_installements,
                    'product_utility_ids': oper.product_utility_ids.id,
                    'no_of_installements': 1,
                    'display_type': 'default',
                    'recerv_unit': True,
                    'qty_delivered_manual': oper.unit_price,
                    'price_unit': oper.unit_price,
                    'unit_price': round(oper.unit_price, 4),
                    'stop_per': True,
                    'tax_id': False,
                    'install_inv_id': oper.install_inv_id.id,
                })
                order_lines.append((0, 0, sale_line1))
        self.order_line.unlink()
        self.with_context(dd='off').order_line = order_lines
        # so_total_amount = sum(self.order_line.mapped('price_subtotal'))
        # utility_price = sum(
        #     self.unit_id.product_utility_ids.filtered(lambda rec: not rec.included_price).mapped('price'))
        # unit_amount = round(self.total_amount + utility_price, 2)
        # diff = unit_amount - so_total_amount
        # if 0 < diff < 1:
        #     last_line = self.order_line[-1]
        #     if last_line:
        #         last_line.unit_price += diff
        # else:
        #     diff = so_total_amount - unit_amount
        #     if 0 < diff < 1:
        #         last_line = self.order_line[-1]
        #         if last_line:
        #             last_line.unit_price -= diff

    def calc_line_amount_without_fraction(self, installment_no, installment_amount):
        all_amount = installment_amount * installment_no
        fraction = round(all_amount % installment_no, 6)
        all_amount_without_fraction = all_amount - fraction
        line_amount = all_amount_without_fraction / installment_no
        return line_amount, fraction

    def action_view_invoice_units(self):
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('real_estate.account_invoice_groupby_inherit_sales').id
        return {
            'name': "Invoices",
            'domain': [('sale_order', '=', self.id)],
            'view_mode': 'list,form',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.onchange('payment_plan_id')
    def _onchange_payment_plan_id(self):
        if not self.payment_plan_id:
            return
        payment_plan = self.payment_plan_id
        unit_id = self.unit_id
        order_lines = []
        self.order_line = False
        for line in payment_plan.payment_line_ids:
            amount = (line.percentage * self.total_amount) / 100
            amount_percentage = (amount * line.line_interset) / 100
            sale_line = {
                'percentage': line.percentage,
                'value': line.value,
                'schedule_period': line.schedule_period,
                'duration': line.duration,
                'pay_type': line.pay_type,
                'name': self.unit_id.name,
                'product_id': self.unit_id.id,
                'product_uom': self.unit_id.uom_id.id,
                'product_uom_qty': line.no_of_installements,
                'no_of_installements': line.no_of_installements,
                'display_type': 'default',
                'is_expense': False,
                'amount_percentage': amount_percentage,
                'interset': line.line_interset,
                'qty_delivered_manual': amount_percentage + (
                        (line.percentage * self.total_amount) / 100) / line.no_of_installements,

                # 'price_unit': (amount_percentage + amount) / line.no_of_installements,
                'unit_price': (amount_percentage + amount) / line.no_of_installements,
                'tax_id': False,
            }
            if line.pay_type == 'reservation':
                sale_line.update({'recerv_unit':True})
            order_lines.append((0, 0, (sale_line)))
        for utility in unit_id.product_utility_ids:
            if utility.included_price == False:
                if utility.payment_plan_id:
                    for plan in utility.payment_plan_id.payment_line_ids:
                        amount_utility = (plan.percentage * utility.price) / 100
                        amount_percentage_utility = (amount_utility * plan.line_interset) / 100
                        utility_line = ({
                            'percentage': plan.percentage,
                            'value': plan.value,
                            'schedule_period': plan.schedule_period,
                            'duration': plan.duration,
                            'pay_type': plan.pay_type,
                            'name': utility.name.name,
                            'product_utility_ids': utility.id,
                            'product_id': self.unit_id.id,
                            'product_uom': self.unit_id.uom_id.id,
                            'product_uom_qty': plan.no_of_installements,
                            'no_of_installements': plan.no_of_installements,
                            'display_type': 'default',
                            'interset': plan.line_interset,
                            'is_expense': False,
                            'amount_percentage': amount_percentage_utility / plan.no_of_installements,
                            'qty_delivered_manual': (amount_percentage_utility / plan.no_of_installements) + (
                                    (plan.percentage * utility.price) / 100) / plan.no_of_installements,
                            # 'price_unit': (amount_percentage_utility / plan.no_of_installements) + (
                            #         (plan.percentage * utility.price) / 100) / plan.no_of_installements,
                            'unit_price': (amount_percentage_utility / plan.no_of_installements) + (
                                    (plan.percentage * utility.price) / 100) / plan.no_of_installements,
                            'tax_id': False,
                        })
                        order_lines.append((0, 0, utility_line))
        self.order_line = order_lines
        self.unit_id = unit_id
        self.payment_plan_id = payment_plan

    def _action_confirm(self):
        for unit in self:
            self.unit_id.analytic_account_id.partner_id = self.partner_id
            self.unit_id.state = 'sold'
            self.unit_id.confirm_date = fields.Date.today()
            self.unit_id.customer_id = self.partner_id
        if len(self.order_line) > 0:
            self.state = 'sale'
        else:
            raise ValidationError("Please Add Product In Sale Order")
        self.state = 'sent'
        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
        })
        if self.env.context.get('send_email'):
            self.force_quotation_send()

        # create an analytic account if at least an expense product
        if any([expense_policy != 'no' for expense_policy in self.order_line.mapped('product_id.expense_policy')]):
            if not self.analytic_account_id:
                self._create_analytic_account()
        else:
            pass
        return True

    @api.depends('unit_id','unit_id.payment_plan_id')
    def get_unit_payment_plan_id(self):
        for rec in self:
            rec.unit_payment_plan_id = rec.unit_id.payment_plan_id.ids

    # @api.onchange('unit_id')
    # def _get_payment_plan_id(self):
    #     planlist = []
    #     if not self.unit_id:
    #         self.payment_plan_id = 0
    #     if self.unit_id:
    #         for plan in self.unit_id.payment_plan_id:
    #             planlist.append(plan.id)
    #         return {'domain': {'payment_plan_id': [('id', 'in', planlist)]}}

    partner_id = fields.Many2one(comodel_name='res.partner',)

    unit_delivery_date = fields.Date('Unit Delivery Date')
    check_ids = fields.One2many(comodel_name="account.payment", inverse_name="so_id", string="Checks",
                                required=False, )
    checks_count = fields.Integer('Checks', compute="compute_checks_count", default=0)

    @api.depends('check_ids')
    def compute_checks_count(self):
        for rec in self:
            rec.checks_count = len(rec.check_ids)

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
            # 'contract_date': fields.Date.today()
        }

    def action_confirm(self):
        if self.unit_id and not self.inv_calc_payment:
            raise exceptions.ValidationError(_('You Should Click Calculate Payment Button First !!'))
        self.action_create_installement()
        res = super(SaleOrderInherited, self).action_confirm()
        return res
    @api.model
    def default_get(self, fields):
        res = super(SaleOrderInherited, self).default_get(fields)
        res['pricelist_id'] = self.env['product.pricelist'].sudo().search([],limit=1).id
        return res

    def action_view_checks(self):
        return {
            'name': "Checks",
            'domain': ['|', ('so_id', '=', self.id), ('offer_id', '=', self.id)],
            'context': {
                'create': True,
            },
            'view_mode': 'list,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
    # def action_send_notification(self,user):
    #     baseDate = fields.Date.today(self)
    #     self._activity_schedule_with_view(
    #         'mail.mail_activity_data_todo',
    #         views_or_xmlid='real_estate.sale_order_view_tree_inherit_crm',
    #         date_deadline = baseDate,
    #         summary = 'Lead Assign',
    #         user_id=user,
    #             render_context={
    #                 'orders':self,
    #         }
    #     )
    #     # activity = self.env['mail.activity'].create({
    #     #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
    #     #     'user_id': user,
    #     #     'date_deadline': baseDate,
    #     #     'summary':'Lead Assign',
    #     #     'res_id': self.id,
    #     #     'res_model_id': self.env['ir.model']._get('sale.order').id,
    #     # })
    def sales_reserve_approve(self):
        self.state = 'sales_reserve_approve'
        # self.action_send_notification(self.user_id.id)
        # if self.sale_person2_id:
        #     self.action_send_notification(self.sale_person2_id.id)
        # if self.sale_person3_id:
        #     self.action_send_notification(self.sale_person3_id.id)

    # def sales_hold_approve(self):
    #     self.state = 'sales_hold_approve'
    #
    def accounting_reserve_approve(self):
        self.state = 'reservation'
        self.unit_id.state = 'hold'

    def action_reject_hold(self):
        self.state = 'draft'
        self.unit_id.state = 'sale'

    def automate_unit_reservation(self):
        for offer in self.env['sale.order'].search([('state','=','reservation')]):
            if offer.unreserve_date and offer.unreserve_date <= fields.datetime.now():
                offer.state = 'draft'
                offer.unit_id.action_back_to_sale_product()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrderInherited, self).fields_view_get(view_id, view_type, toolbar=toolbar,
                                                                  submenu=False)
        doc = etree.XML(res['arch'])
        fields = res.get('fields')
        if not self.env.user.has_group('real_estate.edit_offer_line_group'):
            if view_type in ['form']:
                for field in fields:
                    if field == 'order_line':
                        for node in doc.xpath("//field[@name='%s']" % field):
                            modifiers = json.loads(node.get("modifiers"))
                            modifiers['readonly'] = True
                            node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc)
        return res



class payment_batch(models.Model):
    _inherit = 'account.batch.payment'

    arabic_amount_unit = fields.Char(compute='_compute_arabic_amount_unit', store=True)

    @api.depends('amount')
    def _compute_arabic_amount_unit(self):
        for line in self:
            line.arabic_amount_unit = amount_to_text_ar(line.amount, line.currency_id.symbol)