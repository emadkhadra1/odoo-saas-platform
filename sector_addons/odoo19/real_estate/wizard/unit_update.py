# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare


class wizard_model(models.TransientModel):
    _name = 'unit.update'
    _description = 'Unit Update'

    unit_area = fields.Float(string="Unit Area", required=False, )
    land_area = fields.Float(string="Land Area", required=False, )
    extra_land_area = fields.Float(string="Extra Land Area", required=False, )

    unit_meter_price = fields.Monetary(string="Unit Meter Price", required=False, )
    land_meter_price = fields.Monetary(string="Land Meter Price", required=False, )
    extra_land_meter_price = fields.Monetary(string="Extra Land Meter Price", required=False, )
    min_deposit_amount = fields.Monetary(string="Min Deposit Amount", required=False, )

    sale_price = fields.Float(string="Sale Price", required=False, )

    type = fields.Selection(string="Update Method", selection=[
        ('not_direct', 'Update Unit Data Separately'),
        ('direct', 'Update sale Price Direct'),
    ], required=False, default='not_direct')

    currency_id = fields.Many2one(comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    privilege_ids = fields.One2many(comodel_name="update.privilege", inverse_name="update_id", string="",
                                    required=False, )
    utility_ids = fields.One2many(comodel_name="update.utility", inverse_name="update_id", string="",
                                  required=False, )
    product_ids = fields.Many2many(comodel_name="product.template", string="Units",
                                   domain=[('state', 'not in', ['blocked', 'sold'])])

    def action_update_unit_data(self):
        if not self.product_ids:
            raise exceptions.ValidationError('Please Select Units To Update It !!')
        update_vals = {}
        if self.type == 'not_direct':
            if self.unit_area:
                update_vals.update({
                    'total_Area': self.unit_area
                })
            if self.land_area:
                update_vals.update({
                    'land_area': self.land_area
                })
            if self.extra_land_area:
                update_vals.update({
                    'extra_land': self.extra_land_area
                })
            if self.unit_meter_price:
                update_vals.update({
                    'meter_price': self.unit_meter_price
                })
            if self.land_meter_price:
                update_vals.update({
                    'land_meter_price': self.land_meter_price
                })
            if self.extra_land_meter_price:
                update_vals.update({
                    'extra_land_price': self.extra_land_meter_price
                })
            if self.min_deposit_amount:
                update_vals.update({
                    'min_deposit_amount': self.min_deposit_amount
                })
        elif self.type == 'direct':
            if self.sale_price:
                update_vals.update({
                    'list_price': self.sale_price
                })
        for line in self.product_ids:
            line.write(update_vals)
            if self.type == 'not_direct':
                for rec in line.privilege_ids:
                    res = self.privilege_ids.filtered(lambda prev: prev.privilege_id == rec.privilege_id)
                    if res:
                        rec.percent = res.percent
                for uu in line.product_utility_ids:
                    res = self.utility_ids.filtered(lambda utility: utility.utility_id == uu.name)
                    if res:
                        uu.price = res.price
                line.onchange_listprice()


class Privilege(models.TransientModel):
    _name = 'update.privilege'

    privilege_id = fields.Many2one(comodel_name="privilege.privilege", string="Privileges", required=True, )
    percent = fields.Float(string="Percent", required=True)
    update_id = fields.Many2one(comodel_name="unit.update", string="Update", required=False, )


class Utility(models.TransientModel):
    _name = 'update.utility'

    utility_id = fields.Many2one(comodel_name="utility.utility", string="Utility", required=True, )
    price = fields.Float(string="Price", required=True)
    update_id = fields.Many2one(comodel_name="unit.update", string="Update", required=False, )
