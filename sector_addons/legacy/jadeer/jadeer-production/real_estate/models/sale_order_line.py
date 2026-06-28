
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp
from lxml import etree
import json


class SaleOrderLineInherited(models.Model):
    _inherit = "sale.order.line"
    _order = 'start_date'

    name = fields.Char(required=False,string="Description")
    amount_percentage = fields.Float('Interest Amount')
    interset = fields.Float('Interest', digits=(3, 8), default=0.0)
    recerv_unit = fields.Boolean(default=False)
    stop_per = fields.Boolean(default=False)
    readonly = fields.Boolean(default=False)
    max_rec = fields.Boolean(default=False)
    product_utility_ids = fields.Many2one('product.utility', string='Property Utility', )
    unit_price = fields.Float('Unit Price', default=0.0)
    price_unit = fields.Float('Unit Price', related='unit_price',)
    product_uom_qty = fields.Integer(string='Ordered Quantity', related='no_of_installements', default=1)
    pay_type = fields.Selection(
        [('contracting', 'DownPayment'), ('delivery', 'Delivery'),('maintenance','Maintenance'),
         ('installment', 'Installment'),('reservation','Reservation')], default='contracting', string='Type')
    duration = fields.Selection(selection=[('monthly', 'شهرى'), ('quarterly', 'ربع سنوي'),
                                           ('mid', 'نص سنوي'), ('annual', 'سنوي')], required=False, )
    display_type = fields.Selection([
        ('default', "Default"),
        ('line_section', "Section"),
        ('line_note', "Note")], default='default', help="Technical field for UX purpose.")
    product_id = fields.Many2one('product.product', related='order_id.unit_id.product_variant_id'
                                 , default=lambda self: self.env['product.product'].search([('id', '=', 1)]),
                                 string='Product', domain=[('sale_ok', '=', True)], change_default=True,
                                 ondelete='restrict')
    start_date = fields.Date(string="Start Date", )
    no_of_installements = fields.Integer('# Installments', default=1)
    value = fields.Integer('Value')
    percentage = fields.Float('Percentage (%)', )
    schedule_period = fields.Selection([('day', 'Day'), ('month', 'Month')], default='day', string='Unit')

    @api.onchange('product_id', 'order_id.unit_id')
    def get_default_product_id(self):
        if self.order_id.unit_id:
            prod = self.env['product.product'].search([('product_tmpl_id','=',self.order_id.unit_id.id)])[0].id
            self.product_id =prod
                # self.order_id.unit_id.id
            self.product_id_change()
            # self.product_uom = self.order_id.unit_id.uom_id.id

    @api.onchange('duration')
    def onchange_duration(self):
        if self.duration == 'monthly':
            self.value = 1
            self.schedule_period = 'month'
        elif self.duration == 'quarterly':
            self.value = 3
            self.schedule_period = 'month'
        elif self.duration == 'mid':
            self.value = 6
            self.schedule_period = 'month'
        elif self.duration == 'annual':
            self.value = 12
            self.schedule_period = 'month'

    # @api.depends('unit_price','percentage','order_id.total_amount')
    # def compute_no_of_installements(self):
    #     for rec in self:
    #         if not rec.product_utility_ids and rec.unit_price > 0 and rec.pay_type == 'installment':
    #             rec.no_of_installements = ((rec.percentage * rec.order_id.total_amount) / 100) / rec.unit_price
    #         else:
    #             rec.no_of_installements = 1

    # def set_no_of_installements(self):
    #     print("Set # of Installments")

    @api.onchange('product_utility_ids', 'percentage', 'product_id', 'order_id', 'no_of_installements')
    @api.constrains('product_utility_ids', 'percentage', 'product_id', 'order_id', 'no_of_installements')
    def _onchange_product_utility_ids(self):
        for product in self:
            if product.stop_per == False:
                if product.max_rec == True:
                    product.max_rec = False
                else:
                    if product.product_utility_ids and product.percentage > 0.0:
                        utility = (product.percentage * product.product_utility_ids.price) / 100
                        utility_percentage = (utility * product.interset) / 100
                        if product.no_of_installements > 0:
                            product.amount_percentage = utility_percentage
                            product.unit_price = ((product.percentage * product.product_utility_ids.price) / 100) / product.no_of_installements
                            product.price_unit = ((product.percentage * product.product_utility_ids.price) / 100) / product.no_of_installements

                    else:
                        if product.no_of_installements > 0:
                            product.unit_price = ((product.percentage * product.order_id.total_amount) / 100) / product.no_of_installements
                            product.price_unit = ((product.percentage * product.order_id.total_amount) / 100) / product.no_of_installements

                    product.max_rec = True

    @api.onchange('unit_price')
    def _onchange_unit_price(self):
        for product in self:
            product.price_unit = product.unit_price
            if not product.product_utility_ids:
                if product.stop_per == False:
                    if product.max_rec == True:
                        product.max_rec = False
                    else:
                        if product.unit_price > 0:
                            price = product.unit_price
                            if price > 0:
                                product.percentage = (
                                                             price * product.no_of_installements / product.order_id.total_amount) * 100
                            else:
                                product.percentage = 100.0
                            product.max_rec = True
            else:
                if product.stop_per == False:
                    if product.unit_price > 0:
                        price = product.unit_price
                        if price > 0:
                            product.percentage = (
                                                         price * product.no_of_installements / product.product_utility_ids.price) * 100
                        else:
                            product.percentage = 100.0
                        product.max_rec = True

    @api.onchange('product_id', 'percentage')
    def onchange_product_id(self):
        utility_list = self.env['product.utility'].search(
            [('included_price', '=', False), ('product_id', '=', self.product_id.product_tmpl_id.id)])
        return {'domain': {'product_utility_ids': [('id', 'in', utility_list.ids)]}}

    @api.depends('state', 'is_expense')
    def _compute_qty_delivered_method(self):
        """ Sale module compute delivered qty for product [('type', 'in', ['consu']), ('service_type', '=', 'manual')]
                - consu + expense_policy : analytic (sum of analytic unit_amount)
                - consu + no expense_policy : manual (set manually on SOL)
                - service (+ service_type='manual', the only available option) : manual

            This is true when only sale is installed: sale_stock redifine the behavior for 'consu' type,
            and sale_timesheet implements the behavior of 'service' + service_type=timesheet.
        """
        for line in self:
            if line.display_type != 'default':
                if line.is_expense:
                    line.qty_delivered_method = 'analytic'
                else:  # service and consu
                    line.qty_delivered_method = 'manual'
            else:
                line.qty_delivered_method = 'manual'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for rec in self:
            rec.tax_id = False
        super(SaleOrderLine, self)._compute_amount()

    price_unit = fields.Float(digits=(16, 6))
    price_subtotal = fields.Monetary(digits=(16, 6))
    install_inv_id = fields.Many2one('account.move')

    # price_unit = fields.Float(digits='Product Price')
    # price_subtotal = fields.Monetary(digits='Product Price')
