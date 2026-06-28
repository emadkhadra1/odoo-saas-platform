from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_sequence_id = fields.Many2one(comodel_name="ir.sequence",string="Send Payment Sequence",
                                          domain=[('code','ilike','account.payment')])
    receive_payment_sequence_id = fields.Many2one(comodel_name="ir.sequence",string="Receive Payment Sequence",
                                          domain=[('code','ilike','account.payment')])
