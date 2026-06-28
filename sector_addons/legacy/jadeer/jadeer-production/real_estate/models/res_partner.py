# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta




class ResPartnerInherited(models.Model):
    _inherit = "res.partner"

    second_address = fields.Char(string='Second Address')
    country_id = fields.Many2one('res.country', string='Country',readonly=True,related='nationality',store=True)
    nationality = fields.Many2one('res.country',string='Nationality',)
    per_id = fields.Char(string='ID Number',size=14)
    release_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    issue_from = fields.Char(string='Issue From')
    work_phone = fields.Char(string='Work Phone')
    broker = fields.Boolean(string="Broker")
    broker_id_company_type = fields.Selection(selection=[('person', 'Individual'), ('company', 'Company')],compute='get_broker_id_company_type',store=True)
    sales_users_ids = fields.Many2many('res.users')
    partner_international_id = fields.Char(string='International number')
    partner_national_id = fields.Char(string='National id/passport')
    @api.onchange('sales_users_ids')
    def onchange_sales_users_ids(self):
        for rec in self:
            groups = self.env.ref('real_estate.group_all_broker').users
            if groups not in rec.sales_users_ids:
                for group in groups:
                    rec.sales_users_ids = [(4, group.id)]

            if rec.user_id:
                if rec.user_id not in rec.sales_users_ids:
                    rec.sales_users_ids = [(4, rec.user_id.id)]
    @api.depends('company_type')
    def get_broker_id_company_type(self):
        for rec in self:
            rec.broker_id_company_type = rec.company_type

    def_type = fields.Selection([
        ('id', 'ID'),
        ('passport', 'Passport'),
    ], string='ID Type', default='id')
    unit_ids = fields.One2many(comodel_name="product.template", inverse_name="customer_id", string="Units",)
    @api.onchange('expiry_date','release_date')
    def onchange_expiry_date(self):
        for rec in self:
            if rec.expiry_date and rec.release_date:
                if rec.expiry_date <= rec.release_date:
                    rec.expiry_date = False
                    raise ValidationError("Expiry Date must be greater than release date")
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ This method will find Customer names according to its mobile,
        phone, city, email and its job position."""
        if name:
            args = args if args else []
            args.extend([
                '|', ['name', 'ilike', name],
                 ['unit_ids.name', 'ilike', name],
            ])
            name = ''
        return super(ResPartnerInherited, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

class ResUsers(models.Model):
    _inherit = 'res.users'


    def get_all_team_users(self):
        for rec in self:
            sale = rec.env['crm.team'].search([('user_id','=',rec.env.user.id)]).mapped('member_ids').ids
            sale.append(rec.env.user.id)
        return sale

    def get_all_unit_sale_users(self):
        for rec in self:
            sale = rec.env['sale.order'].search(['|',('user_id','=',rec.env.user.id),'|',('sale_person3_id', '=', rec.env.user.id),('sale_person2_id', '=', rec.env.user.id)]).mapped('unit_id').ids
            sale.append(rec.env.user.id)
        return sale

