from odoo import api, fields, models


class RequestDiscountWizard(models.Model):
    _name = 'discount.request.wizard'

    offer_id = fields.Many2one(comodel_name="sale.order")
    unit_id = fields.Many2one(comodel_name="product.template")
    discount_type = fields.Selection(string="Type", selection=[('amount', 'Amount'), ('percent', 'Percentage'),],
                                     default='amount')
    unit_price = fields.Float(related="unit_id.price_before_discount")
    discount_percentage = fields.Float()
    discount_amount = fields.Float()

    def confirm(self):
        discount_req = self.env['discount.request'].create({'offer_id':self.offer_id.id,
                                                           'unit_id':self.unit_id.id,
                                                           'discount_type':self.discount_type,
                                                           'discount_percentage':self.discount_percentage,
                                                           'discount_amount':self.discount_amount,
                                                           })
        self.offer_id.discount_request_id = discount_req.id


class RequestDiscount(models.Model):
    _name = 'discount.request'

    name = fields.Char()
    offer_id = fields.Many2one(comodel_name="sale.order")
    unit_id = fields.Many2one(comodel_name="product.template")
    discount_type = fields.Selection(string="Type", selection=[('amount', 'Amount'), ('percent', 'Percentage'),],
                                     default='amount')
    unit_price = fields.Float(related="unit_id.price_before_discount")
    discount_percentage = fields.Float()
    discount_amount = fields.Float()
    price_after_disc = fields.Float(compute='compute_price_after_disc')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('first_approval', 'First Approval'),
                                        ('second_approval', 'Second Approval'),
                                        ('approved', 'Approved'),
                                        ('rejected', 'Rejected'),
                                        ],default='draft')

    def name_get(self):
        return [(template.id, '%s' % template.offer_id.name)
                for template in self]

    def action_first_approve(self):
        self.state = 'first_approval'

    def action_second_approval(self):
        self.state = 'second_approval'

    def action_approved(self):
        self.state = 'approved'
        self.unit_id.apply_discount = True
        self.unit_id.discount_type = 'amount' if self.discount_type == 'amount' else 'percentage'
        self.unit_id.discount_percentage = self.discount_percentage
        self.unit_id.discount_amount = self.discount_amount
        self.unit_id.onchange_listprice()
        self.offer_id._onchange_payment_plan_id()

    def action_reject(self):
        self.state = 'rejected'
        self.offer_id.discount_request_id = False

    @api.depends('unit_id','unit_id.price_before_discount',
                  'discount_type', 'discount_amount',
                  'discount_percentage')
    def compute_price_after_disc(self):
        for rec in self:
            price = rec.unit_id.price_before_discount
            if rec.discount_type == 'amount':
                price_after_disc = price - rec.discount_amount
            else:
                price_after_disc = price - (rec.discount_percentage / 100 * price)
            rec.price_after_disc = price_after_disc

