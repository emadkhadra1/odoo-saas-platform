# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from lxml import etree
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, tools, SUPERUSER_ID


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    notify_sale_person1 = fields.Many2one(comodel_name="res.users")
    notify_sale_person2 = fields.Many2one(comodel_name="res.users")
    notify_sale_person3 = fields.Many2one(comodel_name="res.users")
    notify_sale_leader1 = fields.Many2one(comodel_name="crm.team")
    notify_sale_leader2 = fields.Many2one(comodel_name="crm.team")
    notify_sale_leader3 = fields.Many2one(comodel_name="crm.team")
    def sales_persons_notifications(self,users,res_id,summary):
        for user in users:
            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'user_id': user,
                'res_id': res_id,
                'type':'request',
                'summary': summary,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'crm.lead')],
                                                            limit=1).id,
            })

    @api.constrains('user_id','sale_person2_id','sale_person3_id')
    def sales_persons_notifications_action(self):
        for rec in self:
            users = []

            if rec.user_id and  rec.user_id != rec.notify_sale_person1 :
                    users.append(rec.user_id.id)
                    rec.notify_sale_person1 = rec.user_id.id
                    if rec.team_id:
                        users.append(rec.team_id.user_id.id)
                        rec.notify_sale_leader1 = rec.team_id.id
            if rec.sale_person2_id and  rec.sale_person2_id != rec.notify_sale_person2 :
                    users.append(rec.sale_person2_id.id)
                    rec.notify_sale_person2 = rec.sale_person2_id.id

                    if rec.sales_person2_sale_team:
                        users.append(rec.sales_person2_sale_team.user_id.id)
                        rec.notify_sale_leader2 = rec.sales_person2_sale_team.id
            if rec.sale_person3_id and  rec.sale_person3_id != rec.notify_sale_person3 :
                    users.append(rec.sale_person3_id.id)
                    rec.notify_sale_person3 = rec.sale_person3_id.id

                    if rec.sales_person3_sale_team:
                        users.append(rec.sales_person3_sale_team.user_id.id)
                        rec.notify_sale_leader3 = rec.sales_person3_sale_team.id
            if len(users) > 0:
                    self.sales_persons_notifications(users,rec.id,'Lead Assigned')
                    res_users = self.env['res.users'].search([('id', 'in', users)])
                    for notify in res_users:
                        notify.notify_info(message=f'Lead {rec.name} Assigned', title='Lead Assigned', sticky=True,
                                            target=notify.partner_id)


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    def action_apply(self):
        super(Lead2OpportunityPartner, self).action_apply()
        users = []
        if self.lead_id.user_id:
            users.append(self.lead_id.user_id.id)
        if self.lead_id.sale_person2_id:
            users.append(self.lead_id.sale_person2_id.id)
        if self.lead_id.sale_person3_id:
            users.append(self.lead_id.sale_person3_id.id)
        ### team leader members
        if self.lead_id.team_id.user_id:
            users.append(self.lead_id.team_id.user_id.id)
        if self.lead_id.sales_person2_sale_team.user_id:

            users.append(self.lead_id.sales_person2_sale_team.user_id.id)
        if self.lead_id.sales_person3_sale_team.user_id:
            users.append(self.lead_id.sales_person3_sale_team.user_id.id)
        if len(users) > 0:
            self.lead_id.sales_persons_notifications(users, self.lead_id.id, 'Lead Converted to opportunity Assigned')
class Followers(models.Model):
   _inherit = 'mail.followers'

   @api.model
   def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search([('res_model', '=',vals.get('res_model')),
                                           ('res_id', '=', vals.get('res_id')),
                                           ('partner_id', '=', vals.get('partner_id'))])
            if len(dups):
                for p in dups:
                    p.unlink()
        return super(Followers, self).create(vals)