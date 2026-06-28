# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class ProductRequest(models.Model):
    _name = 'product.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    hold_type = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ], track_visibility='onchange', default='automatic')
    active = fields.Boolean(default=True)
    product_id = fields.Many2one('product.template', string='Property Name', track_visibility='onchange', required=True,
                                 readonly=True,
                                 )
    customer_id = fields.Many2one('res.partner', string='Customer', track_visibility='onchange', )
    sales_person_id = fields.Many2one('res.users', string='Sales Person',
                                      track_visibility='onchange', readonly=True, default=lambda self: self.env.user)
    hold_reason = fields.Text(string='Hold Reason', required=True, )
    header_inv = fields.Boolean(default=False)
    hold_days = fields.Integer(string='Hold Days', default=2)
    name = fields.Char('Hold Request', required=True, index=True, copy=False, default='New')
    state = fields.Selection([('request', 'Request'),
                              ('approve', 'Approve'),
                              ('reject', 'Reject')], default='request')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('product.request') or '/'
        return super(ProductRequest, self).create(vals)

    def action_approve_request(self):
        self.product_id.state = 'hold'
        self.product_id.customer_id = self.customer_id.id
        self.product_id.requset_id= self.id
        self.product_id.hold_date = datetime.date.today()
        self.state = 'approve'
        history_line_ids = self.env['product.history'].create({
            'product_id': self.product_id.id,
            'state': 'hold_approve',
            'confirm_date': datetime.datetime.now(),
        })

        requests_list = self.env['product.request'].search([('id', '!=', self.id),('product_id', '=', self.product_id.id)])
        if requests_list:
            for request in requests_list:
                request.action_reject_request()
                request.active = False


    def action_reject_request(self):
        # self.product_id.request_id = False
        self.state = 'reject'
        history_line_ids = self.env['product.history'].create({
            'product_id': self.product_id.id,
            'state': 'hold_rejected',
            'confirm_date': datetime.datetime.now(),
        })

    def close_dialog(self):
        history_line_ids = self.env['product.history'].create({
            'product_id': self.product_id.id,
            'state': 'hold',
            'confirm_date': datetime.datetime.now(),
        })
        all_groups = self.env['res.groups'].search([])
        groups = self.env.ref('real_estate.group_unit_hold_request').users
        if groups:
            users_ids = self.env['res.users'].sudo().search_read(
                [('id', 'in', groups.ids)])
            partners_list = []
            if users_ids:
                for user in users_ids:
                    partners_list.append(user['id'])

            partner_ids = self.env['res.partner'].search(
                [('user_id', 'in', partners_list)])

            send_partners_ids = []

            if partner_ids:
                for partner in partner_ids:
                    send_partners_ids.append(partner['id'])

            body = str(self.sales_person_id.name) + ' Creates New Request For Unit' + str(self.product_id.name)

            msg2 = self.env['mail.message'].create({
                'subject': ' New Request ',
                'body': body,
                'author_id': self.env.user.partner_id.id,
                'partner_ids': [(6, 0, send_partners_ids)],
                'message_type': 'email',
                # 'needaction_partner_ids': [(6, 0, send_partners_ids)],
                # 'moderation_status': 'pending_moderation',

            })
            self.action_approve_request()
            # self.product_id.notify_onchange_state()

        # return {'type': 'ir.actions.act_window_close'}
