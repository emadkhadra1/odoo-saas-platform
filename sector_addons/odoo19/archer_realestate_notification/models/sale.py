# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, tools, SUPERUSER_ID, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def sales_persons_notifications(self, users, res_id, summary):

        for user in users:
            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'user_id': user,
                'res_id': res_id,
                'type': 'request',
                'summary': summary,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'sale.order')],
                                                                   limit=1).id,
            })

    def sales_persons_notifications_action(self):
        for rec in self:
            users = []
            if rec.user_id:
                users.append(rec.user_id.id)
                users.append(rec.team_id.user_id.id)
            if rec.sale_person2_id:
                users.append(rec.sale_person2_id.id)
                users.append(rec.sale_person2_sale_team.user_id.id)
            if rec.sale_person3_id:
                users.append(rec.sale_person3_id.id)
                users.append(rec.sale_person3_sale_team.user_id.id)
            if rec.state != 'sales_reserve_approve':
                for user in self.env.ref('archer_realestate_notification.group_sale_director').users:
                    if user.id not in users:
                        users.append(user.id)
                # for user in self.env.ref('archer_realestate_notification.group_cfo_director').users:
                #     if user.id not in users:
                #         users.append(user.id)

            if len(users) > 0:
                self.sales_persons_notifications(users, rec.id, f'Reserve Request Approved by {self.env.user.name}')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {rec.name} Approved by {self.env.user.name}',
                                       title='Reserve Request Approved', sticky=True,
                                       target=notify.partner_id)
    def cfo_notifications_action(self):
        for rec in self:
            users = []
            for cfo in self.env.ref('archer_realestate_notification.group_cfo_director').users:
                if cfo.id not in users:
                    users.append(cfo.id)
            if len(users) > 0:
                self.sales_persons_notifications(users, rec.id, f'Offer {rec.name} Cancel Request Waiting Approve')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {self.name} Cancel Request Waiting Approve',
                                       title='Offer Cancel request',
                                       sticky=True,
                                       target=notify.partner_id)
    def accounting_notifications_action(self):
        for rec in self:
            users = []
            for inv in self.env.ref('account.group_account_invoice').users:
                if inv.id not in users:
                    users.append(inv.id)
            if len(users) > 0:
                self.sales_persons_notifications(users, rec.id, f'Offer {rec.name} Cancel Request Waiting Approve')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {self.name} Cancel Request Waiting Approve',
                                       title='Offer Cancel request',
                                       sticky=True,
                                       target=notify.partner_id)
    def action_sales_director_cancel(self):
        super(SaleOrder, self).action_sales_director_cancel()
        self.accounting_notifications_action()

    def action_accounting_approve(self):
        super(SaleOrder, self).action_accounting_approve()
        self.cfo_notifications_action()


    def action_reserve_unit(self):
        group_treasury_users = []
        for user in self.env.ref('archer_realestate_notification.group_treasury').users:
            group_treasury_users.append(user.id)
        if len(group_treasury_users) > 0:
            self.sales_persons_notifications(group_treasury_users, self.id, 'Offer Payment Need Action')
            res_users = self.env['res.users'].search([('id', 'in', group_treasury_users)])
            for notify in res_users:
                notify.notify_info(message=f'Offer {self.name} Payment amount {self.hold_amount} Need Action',
                                   title='Offer Payment',
                                   sticky=True,
                                   target=notify.partner_id)
        self.sales_persons_notifications_action()
        super(SaleOrder, self).action_reserve_unit()


    def action_notify_done_deal(self):
        users = []
        for rec in self:
            if rec.user_id:
                if rec.user_id.id not in users:
                    users.append(rec.user_id.id)
                    users.append(rec.team_id.user_id.id)
            if rec.sale_person2_id:
                if rec.sale_person2_id.id not in users:
                    users.append(rec.sale_person2_id.id)
                    users.append(rec.sale_person2_sale_team.user_id.id)
            if rec.sale_person3_id:
                if rec.sale_person3_id.id not in users:
                    users.append(rec.sale_person3_id.id)
                    users.append(rec.sale_person3_sale_team.user_id.id)
            for user in self.env.ref('archer_realestate_notification.group_sale_director').users:
                if user.id not in users:
                    users.append(user.id)
            for tru in self.env.ref('archer_realestate_notification.group_treasury').users:
                if tru.id not in users:
                    users.append(tru.id)
            for inv in self.env.ref('account.group_account_invoice').users:
                if inv.id not in users:
                    users.append(inv.id)
            for cfo in self.env.ref('archer_realestate_notification.group_cfo_director').users:
                    if cfo.id not in users:
                        users.append(cfo.id)
            if len(users) > 0:
                self.sales_persons_notifications(users, rec.id, f'Offer Done Deal')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {rec.name} Done Deal', title='Offer Done Deal',
                                       sticky=True,
                                       target=notify.partner_id)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.action_notify_done_deal()

    def sales_reserve_approve(self):
        self.sales_persons_notifications_action()
        super(SaleOrder, self).sales_reserve_approve()

    def action_notify_downpayment(self):
        users = []
        for rec in self:
            if rec.user_id:
                if rec.user_id.id not in users:
                    users.append(rec.user_id.id)
                    users.append(rec.team_id.user_id.id)
            if rec.sale_person2_id:
                if rec.sale_person2_id.id not in users:
                    users.append(rec.sale_person2_id.id)
                    users.append(rec.sale_person2_sale_team.user_id.id)
            if rec.sale_person3_id:
                if rec.sale_person3_id.id not in users:
                    users.append(rec.sale_person3_id.id)
                    users.append(rec.sale_person3_sale_team.user_id.id)
            for user in self.env.ref('archer_realestate_notification.group_treasury').users:
                if user.id not in users:
                    users.append(user.id)
            for user in self.env.ref('account.group_account_invoice').users:
                if user.id not in users:
                    users.append(user.id)
            for cfo in self.env.ref('archer_realestate_notification.group_cfo_director').users:
                    if cfo.id  in users:
                        users.remove(cfo.id)
            if len(users) > 0:
                self.sales_persons_notifications(users, rec.id, f'Offer {rec.name} Down Payment')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {rec.name}', title='Offer Down Payment Request',
                                       sticky=True,
                                       target=notify.partner_id)

    def action_make_down_payment(self):
        self.action_notify_downpayment()
        super(SaleOrder, self).action_make_down_payment()


class ReserveRequest(models.TransientModel):
    _inherit = 'reserve.request.wizard'

    def sales_persons_notifications_action(self):
        for rec in self:
            users = []
            if rec.offer_id.user_id:
                users.append(rec.offer_id.user_id.id)
                users.append(rec.offer_id.team_id.user_id.id)
            if rec.offer_id.sale_person2_id:
                users.append(rec.offer_id.sale_person2_id.id)
                users.append(rec.offer_id.sale_person2_sale_team.user_id.id)
            if rec.offer_id.sale_person3_id:
                users.append(rec.offer_id.sale_person3_id.id)
                users.append(rec.offer_id.sale_person3_sale_team.user_id.id)
            for user in self.env.ref('archer_realestate_notification.group_sale_director').users:
                if user.id not in users:
                    users.append(user.id)
            for user in self.env.ref('archer_realestate_notification.group_treasury').users:
                if user.id not in users:
                    users.append(user.id)
            for user in self.env.ref('account.group_account_invoice').users:
                if user.id not in users:
                    users.append(user.id)
            for cfo in self.env.ref('archer_realestate_notification.group_cfo_director').users:
                    if cfo.id  in users:
                        users.remove(cfo.id)

            if len(users) > 0:
                self.offer_id.sales_persons_notifications(users, rec.offer_id.id, 'Reserve Request')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {self.offer_id.name} ,amount {self.amount}',
                                       title='Offer reserve request',
                                       sticky=True,
                                       target=notify.partner_id)

    def confirm(self):
        super(ReserveRequest, self).confirm()
        self.sales_persons_notifications_action()


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def validate_move(self):
        if self._context.get('active_model') == 'account.move':
            domain = [('id', 'in', self._context.get('active_ids', [])), ('state', '=', 'draft')]
        elif self._context.get('active_model') == 'account.journal':
            domain = [('journal_id', '=', self._context.get('active_id')), ('state', '=', 'draft')]
        else:
            raise UserError(_("Missing 'active_model' in context."))

        moves = self.env['account.move'].search(domain).filtered('line_ids')
        if not moves:
            raise UserError(_('There are no journal items in the draft state to post.'))
        contract_date = moves.mapped('sale_order').mapped('contract_date')
        if contract_date and any(date == False for date in contract_date):
            raise UserError(_('Please Enter Contract Date'))
        moves._post(not self.force_post)
        return {'type': 'ir.actions.act_window_close'}
class CancelReasonUnitWizard(models.TransientModel):
    _inherit = 'cancel.reason.wizard'
    def sales_director_notifications_action(self):
        for rec in self:
            users = []
            for user in self.env.ref('archer_realestate_notification.group_sale_director').users:
                if user.id not in users:
                    users.append(user.id)
            if len(users) > 0:
                self.sale_order_id.sales_persons_notifications(users, rec.sale_order_id.id, f'Offer {rec.sale_order_id.name} Cancel Request Waiting Approve')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {self.sale_order_id.name} Cancel Request Waiting Approve',
                                       title='Offer Cancel request',
                                       sticky=True,
                                       target=notify.partner_id)

    def confirm(self):
        super(CancelReasonUnitWizard, self).confirm()
        self.sales_director_notifications_action()