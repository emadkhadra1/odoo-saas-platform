import string

from odoo import api, fields, models, _
from odoo.exceptions import UserError


to_19_ar = (u'صفر', u'واحد', u'اثنان', u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
            u'سبعة', u'ثمانية', u'تسعة', u'عشرة', u'أحد عشر', u'اثنا عشر', u'ثلاثة عشر',
            u'أربعة عشرة', u'خمسة عشر', u'ست عشرة', u'سبعة عشر', u'ثمانية عشر', u'تسعة عشر')

tens_ar = (u'', u'', u'عشرون', u'ثلاثون', u'أربعون', u'خمسون', u'ستون', u'سبعون', u'ثمانون', u'تسعون')

hund_ar = (u'', u'', u'مئتان', u'ثلاثمائة', u'اربعمائة', u'خمسمائة', u'ستمائة', u'سبعمائة',
           u'ثمانمئة', u'تسعمائة')


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
            return to_19_ar[rest] + u' و ' + tens_ar[ten]
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
        hund_text = u'مئة'
    elif hund < 10:
        hund_text = hund_ar[hund]
    else:
        hund_text = convert_less_1000(hund) + u' مئة '
    if rest != 0:
        if hund_text != u'':
            hund_text = hund_text + u' و ' + convert_to_ar(rest)
        else:
            hund_text = convert_to_ar(rest)
    return hund_text


def convert_less_10000(number):
    thous = number / 1000
    rest = number % 1000
    if thous == 0:
        thous_text = u''
    elif thous == 1:
        thous_text = u'الف'
    elif thous == 2:
        thous_text = u'الفان'
    elif thous <= 10:
        thous_text = convert_less_100(thous) + u'آلاف'
    else:
        thous_text = convert_less_1000(thous) + u' الف '
    if rest != 0:
        if thous_text != u'':
            thous_text = thous_text + u' و ' + convert_to_ar(rest)
        else:
            thous_text = convert_to_ar(rest)
    return thous_text


def convert_less_billion(number):
    million = number / 1000000
    rest = number % 1000000
    if million == 1:
        million_text = u'مليون'
    elif million == 2:
        million_text = u'مليونين'
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'ملايين'
    else:
        million_text = convert_less_1000(million) + u' ' + u'مليون'
    if rest != 0:
        million_text = million_text + u' و ' + convert_to_ar(rest)
    return million_text


def convert_over_billion(number):
    million = number / 1000000000
    rest = number % 1000000000
    if million == 1:
        million_text = u'مليار'
    elif million == 2:
        million_text = u'مليارين'
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'مليارات'
    else:
        million_text = convert_less_1000(million) + u' ' + u'مليار'
    if rest != 0:
        million_text = million_text + u' و ' + convert_to_ar(rest)
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

    if start_word == u'واحد':
        currenc = u'جنيها'
    elif start_word in [u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
                        u'سبعة', u'ثمانية', u'تسعة', u'عشرة']:
        currenc = u'جنيهات'
    else:
        currenc = u'جنيها'
    end_word = convert_to_ar(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and u' قرشا ' or u' قرشا '
    final_result = start_word + u' ' + currenc + u' و ' + end_word + u' ' + cents_name
    return final_result


if __name__ == '__main__':
    number = 23539000002.50
    currency = u' جنية مصري '


def amount_to_text_ar_area(number):
    list = str(number).split('.')
    if list:
        start_word = convert_to_ar(abs(int(list[0])))

        if start_word == u'واحد':
            currenc = u'مترا'
        elif start_word in [u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
                            u'سبعة', u'ثمانية', u'تسعة', u'عشرة']:
            currenc = u'امتار'
        else:
            currenc = u'امتار'
        end_word = convert_to_ar(int(list[1]))
        final_result = start_word + u' ' + currenc
        return final_result


if __name__ == '__main__':
    number = 23539000002.50
    currency = u' جنية مصري '

class ResCompany(models.Model):
    _inherit = 'res.company'

    Company_Type = fields.Char(string='Type')


class AccountPaymnt(models.Model):
    _inherit = 'account.payment'

    arabic_amount = fields.Char(compute='_compute_arabic_amount_payment')
    pay_type = fields.Selection(
        [('contracting', 'DownPayment'), ('delivery', 'Delivery'),('maintenance','Maintenance'),
         ('installment', 'Installment'), ('reservation', 'Reservation')], string='Type 2')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        check_company=True, domain="[('id', 'in', suitable_journal_ids)]")

    @api.onchange('journal_id')
    def onchange_payment_journal(self):
        for rec in self:
            rec.move_id.journal_id = rec.journal_id.id

    def write(self, vals):
        res = super(AccountPaymnt, self).write(vals)
        for rec in self:
            if 'journal_id' in vals:
                rec.move_id.journal_id = rec.journal_id.id
        return res

    @api.depends('amount')
    def _compute_arabic_amount_payment(self):
        for line in self:
            line.arabic_amount = amount_to_text_ar(line.amount_company_currency_signed, line.currency_id.symbol)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_address = fields.Char(string='Address')


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    pay_type = fields.Selection(
        [('contracting', 'DownPayment'), ('delivery', 'Delivery'),('maintenance','Maintenance'),
         ('installment', 'Installment'), ('reservation', 'Reservation')], default='contracting', string='Type')

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        move = False
        if self._context.get('active_model') == 'account.move':
            move = self.env['account.move'].browse(self._context.get('active_ids', []))
        elif self._context.get('active_model') == 'account.move.line':
            lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
            move = lines.mapped('move_id')
        if move and 'pay_type' in fields_list:
            res['pay_type'] = move.pay_type

        if 'line_ids' in fields_list and 'line_ids' not in res:

            # Retrieve moves to pay from the context.

            if self._context.get('active_model') == 'account.move':
                lines = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids
            elif self._context.get('active_model') == 'account.move.line':
                lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
            else:
                raise UserError(_(
                    "The register payment wizard should only be called on account.move or account.move.line records."
                ))

            if 'journal_id' in res and not self.env['account.journal'].browse(res['journal_id']) \
                    .filtered_domain([('company_id', '=', lines.company_id.id), ('type', 'in', ('bank', 'cash'))]):
                # default can be inherited from the list view, should be computed instead
                del res['journal_id']

            # Keep lines having a residual amount to pay.
            available_lines = self.env['account.move.line']
            for line in lines:
                if line.move_id.state != 'posted':
                    raise UserError(_("You can only register payment for posted journal entries."))

                if line.account_internal_type not in ('receivable', 'payable'):
                    continue
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    if line.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines |= line

            # Check.
            if not available_lines:
                raise UserError(
                    _("You can't register a payment because there is nothing left to pay on the selected journal items."))
            if len(lines.company_id) > 1:
                raise UserError(_("You can't create payments for entries belonging to different companies."))
            if len(set(available_lines.mapped('account_internal_type'))) > 1:
                raise UserError(
                    _("You can't register payments for journal items being either all inbound, either all outbound."))

            res['line_ids'] = [(6, 0, available_lines.ids)]

        return res

    def _create_payment_vals_from_wizard(self):
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals.update({
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'pay_type': self.pay_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id
        })

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals

    @api.depends('can_edit_wizard', 'company_id')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = False
            # if wizard.can_edit_wizard:
            #     batch = wizard._get_batches()[0]
            #     wizard.journal_id = wizard._get_batch_journal(batch)
            # else:
            #     wizard.journal_id = self.env['account.journal'].search([
            #         ('type', 'in', ('bank', 'cash')),
            #         ('company_id', '=', wizard.company_id.id),
            #     ], limit=1)


