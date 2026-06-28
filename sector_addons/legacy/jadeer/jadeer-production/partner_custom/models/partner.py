# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
class CRMLead(models.Model):
    _inherit = 'res.partner'
    national_no = fields.Char('National Number')

    lead_customer = fields.Boolean('Lead/Customer')
    lead_type = fields.Selection(string="Lead Type", selection=[('inbound', 'Inbound'),
                                                                ('outbound', 'Outbound'),
                                                                ('walk_in', 'Walk-in')], default='inbound')
    mobile2 = fields.Char('Mobile 2')
    date_of_birth = fields.Date()
    age = fields.Float(compute="compute_age")

    @api.depends('date_of_birth')
    def compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = fields.date.today()
                rec.age = today.year - rec.date_of_birth.year - ((today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day))
            else:
                rec.age = 0

    @api.constrains('mobile2','mobile','phone')
    def check_duplicate(self):
        customers = self.env['res.partner']
        for rec in self:
            if rec.customer_rank or rec.supplier_rank:
                if rec.phone:
                    customers = self.env['res.partner'].search(
                        [('id', '!=', rec.id),'|',('phone', '=', self.phone),'|', ('mobile', '=', self.phone), ('mobile2', '=', self.phone)])
                    customers = customers.filtered(lambda x:x.supplier_rank or x.customer_rank)
                    if customers:
                        raise exceptions.ValidationError('This number:{} repeated on another partner'.format(rec.phone))
                if rec.mobile:
                    customers = self.env['res.partner'].search(
                        [ ('id', '!=', rec.id),'|',('mobile', '=', self.mobile),'|',('phone', '=', self.mobile),('mobile2', '=', self.mobile)])
                    customers = customers.filtered(lambda x: x.supplier_rank or x.customer_rank)
                    if customers:
                        raise exceptions.ValidationError('This number:{} repeated on another partner'.format(rec.mobile))
                if rec.mobile2:
                    customers = self.env['res.partner'].search(
                        [('id', '!=', rec.id),'|',('mobile', '=', self.mobile2),'|',('phone', '=', self.mobile2),('mobile2', '=', self.mobile2)])
                    customers = customers.filtered(lambda x: x.supplier_rank or x.customer_rank)
                    if customers:
                        raise exceptions.ValidationError('This number:{} repeated on another partner'.format(rec.mobile2))
