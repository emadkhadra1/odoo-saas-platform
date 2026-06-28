from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    penalty_id = fields.Many2one(comodel_name="product.product", domain="[('is_penalty','=',True)]")
    penalty_type = fields.Selection(selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False, )
    penalty_percentage = fields.Float()
    penalty_amount = fields.Float()
    cancellation_credit_note_id = fields.Many2one(comodel_name="account.move")
    cancellation_reason_id = fields.Many2one(comodel_name="cancel.reason")
    new_unit_id = fields.Many2one(comodel_name="product.template",
                                  domain="[('is_residential', '=',True),('state', '=', 'sale'),]")
    request_downgrade = fields.Boolean()
    request_upgrade = fields.Boolean()
    request_reschedule = fields.Boolean()
    contract_rescheduled = fields.Boolean()
    reschedule_confirmed = fields.Boolean()
    original_contract_id = fields.Many2one(comodel_name="sale.order", string="", required=False, )
    rescheduled_contract_id = fields.Many2one(comodel_name="sale.order",)
    state = fields.Selection(selection_add=[
        ('sales_director_cancel', 'Sales Director Approve'),
        ('accounting_approve', 'Accounting Approve'),
        ('cfo_cancel', 'CFO Approve'),
        ('upgraded', 'Upgraded'),
        ('upgraded', 'Upgraded'),
        ('downgraded', 'Downgraded'),
        ('rescheduled', 'Rescheduled'),

    ])
    def action_sales_director_cancel(self):
        self.write({'state':'accounting_approve'})
    def action_accounting_approve(self):
        if self.is_upgrade:
            self.with_context(hide_downgrade=True).write({'state':'cfo_cancel'})
        elif self.is_downgrade:
            self.with_context(hide_upgrade=True).write({'state':'cfo_cancel'})
        else:
            self.write({'state':'cfo_cancel'})

    def action_accounting_cancel(self):
        if not self.is_upgrade or not self.is_downgrade:
            self.write({'state':'cancel_request'})
        elif self.is_upgrade:
            self.with_context(hidedowngrade=True).write({'state':'cancel_request'})

        else:
            self.with_context(hide_cancel=True).write({'state':'cancel_request'})


    def action_cancel_request(self):
        if self.env['account.move'].search([('move_type','=','out_invoice'),('sale_order','=',self.id)]):
            if not self.penalty_id:
                raise ValidationError("Please Assign Penalty")
        return {
            'name': 'Cancel Request',
            'view_mode': 'form',
            'res_model': 'cancel.reason.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            },
        }

    total_penality = fields.Float(compute='compute_total_pen',store=True)

    @api.depends('amount_total','penalty_type','penalty_percentage')
    def compute_total_pen(self):
        for rec in self:
            penalty_value = 0
            if self.penalty_id:
                if rec.penalty_type == 'percentage':
                    penalty_value = rec.amount_total * rec.penalty_percentage / 100
                else:
                    penalty_value = rec.penalty_amount
            rec.total_penality = penalty_value
    def action_rufus_cancel(self):
        for rec in self:
            if  rec.last_offer_state:
                rec. state = rec.last_offer_state
                rec.is_downgrade = False
                rec.is_upgrade = False
    def create_credit_note(self):
        paid_installment = self.env['account.move'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('sale_order', '=', self.id),
            ('payment_state', 'in', ['in_payment', 'paid', 'partial']),
        ])
        total_installment_paid = 0
        for installment in paid_installment:
            total_installment_paid += (installment.amount_total - installment.amount_residual)
        if total_installment_paid > 0:
            account_id = self.unit_id.property_account_income_id.id or self.unit_id.categ_id.property_account_income_categ_id.id
            if self.penalty_id:
                if self.penalty_type == 'percentage':
                    penalty_value = self.amount_total * self.penalty_percentage / 100
                else:
                    penalty_value = self.penalty_amount
                invoice = self.env['account.move'].create({
                    'move_type': 'out_refund',
                    'partner_id': self.partner_id.id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'product_id': self.unit_id.product_variant_id.id,
                            'name': 'Contract Cancellation',
                            'account_id': account_id,
                            'quantity': 1,
                            'price_unit': total_installment_paid,
                        }),
                        (0, 0, {'product_id': self.penalty_id.id,
                                'name': 'Contract Cancellation',
                                'account_id': self.penalty_id.property_account_income_id.id,
                                'quantity': 1,
                                'price_unit': - penalty_value,
                                })
                    ],
                })
            else:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_refund',
                    'partner_id': self.partner_id.id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'product_id': self.unit_id.product_variant_id.id,
                            'name': 'Contract Cancellation',
                            'account_id': account_id,
                            'quantity': 1,
                            'price_unit': total_installment_paid,
                        }),
                    ],
                })
            self.cancellation_credit_note_id = invoice.id

        not_paid_installment = self.env['account.move'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('sale_order', '=', self.id),
            ('payment_state', 'in', ['not_paid']),
        ])

        for move in not_paid_installment:
            if move.state == 'posted':
                move.button_draft()
                move.button_cancel()
            else:
                move.button_cancel()

    def action_cancel(self):
        self.create_credit_note()
        self.unit_id.state = 'under_review'
        return self.write({'state': 'cancel'})

    def action_down_grade(self):
        if not self.new_unit_id:
            raise ValidationError("Please Assign The New Unit!")
        self.action_cancel()
        self.state = 'downgraded'
        return {
            'name': 'Contract',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref('real_estate.sale_order_view_tree_inherit_crm').id,
            'target': 'current',
            'context': {'default_unit_id': self.new_unit_id.id,
                        'default_partner_id': self.partner_id.id,
                        'default_original_contract_id': self.id,
                        'default_request_downgrade': True
                        },
        }

    is_upgrade = fields.Boolean()
    is_downgrade = fields.Boolean()
    def action_downgrade(self):
        if not self.new_unit_id:
            raise ValidationError("Please Assign The New Unit!")
        self.write({'state':'sales_director_cancel','is_downgrade':True})
    def action_upgrade(self):
        if not self.new_unit_id:
            raise ValidationError("Please Assign The New Unit!")
        self.write({'state':'sales_director_cancel','is_upgrade':True})

    def action_cfo_approve_upgrade(self):
        if self.is_upgrade:
            self.action_cancel()
            self.state = 'upgraded'
            return {
                'name': 'Contract',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'view_id': self.env.ref('real_estate.sale_order_view_tree_inherit_crm').id,
                'target': 'current',
                'context': {'default_unit_id': self.new_unit_id.id,
                            'default_partner_id': self.partner_id.id,
                            'default_original_contract_id': self.id,
                            'default_request_upgrade': True
                            },
            }
        elif self.is_downgrade:
            self.action_cancel()
            self.state = 'downgraded'
            return {
                'name': 'Contract',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'view_id': self.env.ref('real_estate.sale_order_view_tree_inherit_crm').id,
                'target': 'current',
                'context': {'default_unit_id': self.new_unit_id.id,
                            'default_partner_id': self.partner_id.id,
                            'default_original_contract_id': self.id,
                            'default_request_downgrade': True
                            },
            }
        else:
            self.action_cancel()
    def action_cfo_approve_downgrade(self):
        self.action_down_grade()
    def action_upgrade_contract(self):
        if not self.new_unit_id:
            raise ValidationError("Please Assign The New Unit!")
        self.action_cancel()
        self.state = 'upgraded'
        return {
            'name': 'Contract',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref('real_estate.sale_order_view_tree_inherit_crm').id,
            'target': 'current',
            'context': {'default_unit_id': self.new_unit_id.id,
                        'default_partner_id': self.partner_id.id,
                        'default_original_contract_id': self.id,
                        'default_request_upgrade': True
                        },
        }

    def action_reschedule_contract(self):
        remaining_amount = self._compute_remaining_amount()
        return {
            'name': 'Contract',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref('real_estate.sale_order_view_tree_inherit_crm').id,
            'target': 'current',
            'context': {'default_unit_id': self.unit_id.id,
                        'default_partner_id': self.partner_id.id,
                        'default_original_contract_id': self.id,
                        'default_request_reschedule': True,
                        'default_remaining_amount': remaining_amount
                        },
        }

    def confirm_reschedule(self):
        if self.request_reschedule and self.original_contract_id:
            self.original_contract_id.rescheduled_contract_id = self.id
            self.original_contract_id.contract_rescheduled = True
            self.original_contract_id.state = 'rescheduled'
            self.reschedule_confirmed = True
            not_paid_installment = self.env['account.move'].sudo().search([
                ('partner_id', '=', self.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('sale_order', '=', self.original_contract_id.id),
                ('payment_state', 'in', ['not_paid']),
            ])
            for move in not_paid_installment:
                if move.state == 'posted':
                    move.button_draft()
                    move.button_cancel()
                else:
                    move.button_cancel()

