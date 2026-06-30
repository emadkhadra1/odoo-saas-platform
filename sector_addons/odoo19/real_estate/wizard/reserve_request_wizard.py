from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RequestReserve(models.TransientModel):
    _name = 'reserve.request.wizard'

    name = fields.Char()
    offer_id = fields.Many2one(comodel_name="sale.order")
    unit_id = fields.Many2one(comodel_name="product.template")
    amount = fields.Float()

    def confirm(self):
        if self.amount < self.unit_id.min_deposit_amount:
            raise ValidationError("Cant Reserve With amount < Min. Deposit")
        if self.amount < 5000 :
            raise ValidationError("Cant Reserve With Amount Less than 5000")
        self.offer_id.hold_amount = self.amount
        self.offer_id.request_reserve = True
        self.offer_id.state = 'request_reserve'
