from odoo import fields, models, api


class AccountPaymentInherited(models.Model):
    _inherit = "account.payment"
    def persons_notifications(self, users, res_id, summary):
        for user in users:
            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'user_id': user,
                'res_id': res_id,
                'type': 'request',
                'summary': summary,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'account.payment')],
                                                                   limit=1).id,
            })
    def persons_notifications_action(self):
        for rec in self:
            users = []
            for user in self.env.ref('archer_realestate_notification.group_cfo_director').users:
                users.append(user.id)
            for ceo in self.env.ref('archer_realestate_notification.group_ceo').users:
                users.append(ceo.id)
            for op in self.env.ref('archer_realestate_notification.group_operations').users:
                users.append(op.id)
            if len(users) > 0:
                rec.persons_notifications(users, rec.id, f'Payment {rec.name} amount {rec.amount} Confirmed')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Offer {rec.offer_id.name} Payment {rec.name} , Amount {rec.amount} ', title='Payment Confirmed', sticky=True,
                                        target=notify.partner_id)

    def action_post(self):
        self.persons_notifications_action()
        super(AccountPaymentInherited, self).action_post()

class Product(models.Model):
    _inherit = 'product.template'

    def product_activity_notifications(self, users, res_id, summary):

        for user in users:
            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'user_id': user,
                'res_id': res_id,
                'type': 'request',
                'summary': summary,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'product.template')],
                                                                   limit=1).id,
            })

    state_value = fields.Char(compute='get_state_value')

    # @api.depends('duration')
    def get_state_value(self):
        for rec in self:

            dura = dict(self._fields['state'].selection)
            if dura[rec.state]:
                rec.state_value = dura[rec.state]
            else:
                rec.state_value = False

    def notify_onchange_state(self):
        for rec in self:
            users = []
            for user in self.env.ref('archer_realestate_notification.group_operations').users:
                if user.id not in users:
                    users.append(user.id)
            for user in self.env.ref('archer_realestate_notification.group_ceo').users:
                if user.id not in users:
                    users.append(user.id)
            for user in self.env.ref('real_estate_security.group_manager').users:
                if user.id not in users:
                    users.append(user.id)
            if len(users) > 0:
                self.product_activity_notifications(users, rec.id, f'Unit Status Changed to {rec.state}')
                res_users = self.env['res.users'].search([('id', 'in', users)])
                for notify in res_users:
                    notify.notify_info(message=f'Unit {rec.name} Status {rec.state_value}', title='Unit Status',
                                       sticky=True,
                                       target=notify.partner_id)

    states_chnges = fields.Char(compute='notify_status_change', store=True)

    @api.depends('state')
    def notify_status_change(self):
        for rec in self:
            rec.states_chnges = rec.state
            rec.notify_onchange_state()
