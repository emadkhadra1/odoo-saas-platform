# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
from lxml import etree
from odoo.exceptions import ValidationError


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    country_2_id = fields.Many2one(comodel_name="res.country")
    country_1_id = fields.Many2one(comodel_name="res.country",string="Country")
    international_number = fields.Char('International number')
    phone_code = fields.Integer('Country Code',related="country_id.phone_code")
    phone_code_2 = fields.Integer('Country Code',related="country_2_id.phone_code")
    mobile2 = fields.Char('Mobile 2')
    mobile = fields.Char('Mobile 1')
    international_no = fields.Boolean('International Number')
    whatsapp_no = fields.Boolean("Whats App Number")
    actual_visit = fields.Boolean("Actual Visit")
    visit_notes = fields.Text("Last Visit Notes")
    visit_date = fields.Datetime(string="Last Visit Date", required=False, )
    visit_history_ids = fields.One2many('visit.history','lead_id','Visit History')

    communication_notes = fields.Char('Communication Notes')
    user_id = fields.Many2one('res.users',default=False)
    team_id = fields.Many2one('crm.team',default=False)

    def check_duplicate(self):
        customer = self.env['res.partner']
        has_opp = self.env['crm.lead']
        if self.phone:
            has_opp = self.search(
                [('id', 'not in', self.id),'&',('type', '=', 'opportunity'), '|', ('mobile2', '=', self.phone), '|',
                 ('mobile', '=', self.phone), ('phone', '=', self.phone)], limit=1)
            if not has_opp:
                customer = self.env['res.partner'].search(
                    ['|', ('mobile2', '=', self.phone), '|',
                     ('mobile', '=', self.phone), ('phone', '=', self.phone)], limit=1)
            if has_opp:
                return has_opp.partner_id,has_opp
            elif customer:
                return customer,has_opp
        if self.mobile:
            has_opp = self.search(
                [('id', 'not in', self.ids),'&',('type', '=', 'opportunity'), '|', ('mobile2', '=', self.mobile), '|',
                 ('mobile', '=', self.mobile), ('phone', '=', self.mobile)], limit=1)
            if not has_opp:
                customer = self.env['res.partner'].search(
                    ['|', ('mobile2', '=', self.mobile), '|',
                     ('mobile', '=', self.mobile), ('phone', '=', self.mobile)], limit=1)
            if has_opp:
                return has_opp.partner_id,has_opp
            elif customer:
                return customer,has_opp
        if self.mobile2:
            has_opp = self.search(
                [('id', 'not in', self.ids),'&', ('type', '=', 'opportunity'), '|', ('mobile2', '=', self.mobile2),
                 '|', ('mobile', '=', self.mobile2), ('phone', '=', self.mobile2)], limit=1)
            if not has_opp:
                customer = self.env['res.partner'].search(
                    ['|', ('mobile2', '=', self.mobile2),
                     '|', ('mobile', '=', self.mobile2), ('phone', '=', self.mobile2)], limit=1)
            if has_opp :
                return has_opp.partner_id,has_opp
            elif customer:
                return customer,has_opp
        return customer,customer

    @api.onchange('contact_name')
    def _change_contact_name(self):
        for rec in self:
            if rec.contact_name:
                rec.name = rec.contact_name

    @api.constrains('phone', 'mobile', 'mobile2')
    def _check_phone_mobile(self):
        if self.phone:
            res = self.search(
                [('id', 'not in', self.ids), '|', ('mobile2', '=', self.phone), '|',
                 ('mobile', '=', self.phone), ('phone', '=', self.phone)], limit=1)
            if res:
                if res.partner_id and self.partner_id != res.partner_id:
                    raise exceptions.ValidationError(
                        'Phone number already exists , you must link this lead with contact:{}'.format(
                            res.partner_id.name))
                elif not res.partner_id:
                    raise exceptions.ValidationError('Phone number already exists on lead {}!'.format(res.name))
        if self.mobile:
            res = self.search(
                [('id', 'not in', self.ids), '|', ('mobile2', '=', self.mobile), '|',
                 ('mobile', '=', self.mobile), ('phone', '=', self.mobile)], limit=1)
            if res:
                if res.partner_id and self.partner_id != res.partner_id:
                    raise exceptions.ValidationError(
                        'Mobile 1  already exists , you must link this lead with contact:{}'.format(
                            res.partner_id.name))
                elif not res.partner_id:
                    raise exceptions.ValidationError('Mobile 1 already exists on lead {}!'.format(res.name))
        if self.mobile2:
            res = self.search(
                [('id', 'not in', self.ids), '|', ('mobile2', '=', self.mobile2),
                 '|', ('mobile', '=', self.mobile2), ('phone', '=', self.mobile2)], limit=1)
            if res:
                if res.partner_id and self.partner_id != res.partner_id:
                    raise exceptions.ValidationError(
                        'Mobile 2  already exists , you must link this lead with contact:{}'.format(
                            res.partner_id.name))
                elif not res.partner_id:
                    raise exceptions.ValidationError('Mobile 2 already exists on lead {}!'.format(res.name))
    @api.constrains('phone','mobile','mobile2')
    def change_phone_mobile_crm(self):
        for rec in self:
            if rec.phone == (rec.mobile or rec.mobile2):
                raise ValidationError("Please Assign anther Mobile 1 or  Mobile 2 number")
            if rec.mobile == (rec.phone or rec.mobile2):
                raise ValidationError("Please Assign anther phone or  Mobile 2 number")
            if rec.mobile2 == (rec.mobile or rec.phone):
                raise ValidationError("Please Assign anther  phone or  Mobile 1 number")
    @api.constrains('phone', 'mobile', 'mobile2')
    def _check_phone_mobile_mobile2(self):
        if self.phone:
            phone = self.phone.strip().replace('+2', '')
            phone = phone.strip().replace(' ', '')
            if '+' in self.phone:
                raise exceptions.ValidationError("Phone accept numbers only")
            if ' ' in self.phone:
                raise exceptions.ValidationError("Phone accept numbers only")
        if self.mobile:
            mobile = self.mobile.strip().replace('+2', '')
            mobile = mobile.strip().replace(' ', '')
            if '+' in self.mobile:
                raise exceptions.ValidationError("Mobile accept numbers only")
            if ' ' in self.mobile:
                raise exceptions.ValidationError("Mobile accept numbers only")
        if self.mobile2:
            # mobile2 = self.mobile2.strip().replace('+2', '')
            # mobile2 = mobile2.strip().replace(' ', '')
            if '+' in self.mobile2:
                raise exceptions.ValidationError("Mobile 2 accept numbers only")
            if ' ' in self.mobile2:
                raise exceptions.ValidationError("Mobile 2 accept numbers only")
    @api.constrains('mobile')
    def check_mobile_zise(self):
        for rec in self:
            if rec.mobile:
                mobile = str(rec.mobile).replace(" ", "")
                if mobile.startswith('+2'):
                    mobile = mobile[2:]
                if len(mobile) < 11 :
                    raise ValidationError("Mobile Phone should be  11 digit")
                elif len(mobile) > 11:
                    raise ValidationError("Mobile Phone should be 11 digit")
                else:
                    pass
    @api.constrains('mobile2')
    def check_mobile2_zise(self):
        for rec in self:
            if rec.mobile2:
                mobile = str(rec.mobile2).replace(" ", "")
                if mobile.startswith('+2'):
                    mobile = mobile[2:]
                if len(mobile) < 11:
                    raise ValidationError("Mobile Phone should be  11 digit")
                elif len(mobile) > 11:
                    raise ValidationError("Mobile Phone should be 11 digit")
                else:
                    pass
    @api.constrains('phone')
    def check_phone_zise(self):
        for rec in self:
            if rec.phone:
                phone = str(rec.phone).replace(" ", "")
                if phone.startswith('+2'):
                    phone = phone[2:]
                if len(phone) < 8:
                    raise ValidationError("Phone should be  8 digit")
                elif len(phone) > 8:
                    raise ValidationError("Phone should be 8 digit")
                else:
                    pass
    # @api.constrains('phone','mobile','mobile2','country_id','country_id.num_phone_digit',
    #                 'country_2_id','country_2_id.num_phone_digit:')
    # def check_phone_length(self):
    #     if self.country_id and self.country_id.num_phone_digit:
    #         if self.phone and len(self.phone) != self.country_id.num_phone_digit:
    #             raise ValidationError("NO. Of Phone Digits must be %s" % self.country_id.num_phone_digit)
    #         if self.mobile and len(self.mobile) != self.country_id.num_phone_digit:
    #             raise ValidationError("NO. Of Mobile Digits must be %s" % self.country_id.num_phone_digit)
    #         if self.mobile2 and len(self.mobile2) != self.country_2_id.num_phone_digit:
    #             raise ValidationError("NO. Of Mobile 2 Digits must be %s" % self.country_id.num_phone_digit)

    def update_contact_lead(self,values):
        if self.lead_contact_id:
            if 'mobile' in values:
                self.lead_contact_id.mobile1 = self.mobile
            if 'function' in values:
                self.lead_contact_id.function = self.function
            if 'phone' in values:
                self.lead_contact_id.phone = self.phone
            if 'mobile2' in values:
                self.lead_contact_id.mobile2 = self.mobile2
            if 'email_from' in values:
                self.lead_contact_id.email_from = self.email_from
            if 'email_cc' in values:
                self.lead_contact_id.email_cc = self.email_cc
            if 'partner_name' in values:
                self.lead_contact_id.partner_name = self.partner_name
            if 'street' in values:
                self.lead_contact_id.street = self.street
            if 'street2' in values:
                self.lead_contact_id.street2 = self.street2
            if 'website' in values:
                self.lead_contact_id.website = self.website
            if 'zip' in values:
                self.lead_contact_id.zip = self.zip
            if 'city' in values:
                self.lead_contact_id.city = self.city
            if 'state_id' in values:
                self.lead_contact_id.state_id = self.state_id.id
            if 'country_id' in values:
                self.lead_contact_id.country_id = self.country_id.id
            if 'lang_id' in values:
                self.lead_contact_id.lang_id = self.lang_id.id
            if 'tag_ids' in values:
                self.lead_contact_id.tag_ids = self.tag_ids.ids
            if 'user_id' in values:
                self.lead_contact_id.user_id = self.user_id.id

    def button_crm_lead2opportunity_partner(self):
        action = self.env.ref('crm.action_crm_lead2opportunity_partner').read()[0]
        partner,opportunity = self.check_duplicate()
        if opportunity:
            action['context']={
                                'default_user_id':partner.user_id.id,
                                'default_action':'exist',
                                'default_has_opp':True,
                                'default_partner_id':partner.id,
                                # 'default_has_contact': True,
                                'has_opp':opportunity.ids,
                             }
        elif partner:
            action['context'] = {
                'default_user_id': partner.user_id.id,
                'default_action': 'exist',
                'default_has_contact': True,
                'default_partner_id': partner.id,
                'default_name': 'convert',
                'has_contact': opportunity
            }
        else:
            pass
        return action

    def confirm_visit(self):
        return {
            'name': 'Visit Notes',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'visit.notes',
            'context': {'lead_id': self.id},
            'target': 'new',
        }
