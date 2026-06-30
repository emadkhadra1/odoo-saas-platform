from odoo import api, fields, models


class CancelReasons(models.Model):
    _name = 'cancel.reason'

    name = fields.Char()


class CancelReasonWizard(models.TransientModel):
    _name = 'cancel.reason.wizard'

    name = fields.Char()
    cancel_reason_id = fields.Many2one(comodel_name="cancel.reason",)
    sale_order_id = fields.Many2one(comodel_name="sale.order",)

    def confirm(self):
        self.sale_order_id.cancellation_reason_id = self.cancel_reason_id.id
        # self.sale_order_id.state = 'cancel_request'
        self.sale_order_id.state = 'sales_director_cancel'

