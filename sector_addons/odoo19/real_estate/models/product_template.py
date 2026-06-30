# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class FinishingType(models.Model):
    _name = 'finishing.type'
    _description = 'Finishing Type'

    name = fields.Char()


class ProductTemplateInherited(models.Model):
    _inherit = 'product.template'
    # unit_type = fields.Selection(
    #     string="Unit Type",
    #     selection=[
    #         ('residential', 'Residential'),
    #         ('commercial', 'Commercial'),
    #         ('medical', 'Medical'),
    #         ('administrative', 'Administrative'),
    #     ],
    #     required=False, default='residential')

    product_last_state_date = fields.Datetime(string='Last State',compute='get_product_last_state_date',store=True)
    @api.depends('product_history_ids')
    def get_product_last_state_date(self):
        for rec in self:
            last = False
            if rec.product_history_ids:
                history = rec.env['product.history'].search([('product_id','=',rec.id)], limit=1, order='create_date desc')
                last = history.confirm_date

            rec.product_last_state_date = last
    def name_get(self):
        self.browse(self.ids).read(['name', 'default_code'])
        return [(template.id, '%s' % template.name)
                for template in self]

    @api.constrains('company_id')
    def _check_sale_product_company(self):
        """Ensure the product is not being restricted to a single company while
        having been sold in another one in the past, as this could cause issues."""
        target_company = self.company_id
        if target_company:  # don't prevent writing `False`, should always work
            product_data = self.env['product.product'].sudo().with_context(active_test=False).search_read(
                [('product_tmpl_id', 'in', self.ids)], fields=['id'])
            product_ids = list(map(lambda p: p['id'], product_data))
            so_lines = self.env['sale.order.line'].sudo().search_read(
                [('product_id', 'in', product_ids), ('company_id', '!=', target_company.id)],
                fields=['id', 'product_id'])
            used_products = list(map(lambda sol: sol['product_id'][1] if sol['product_id'] else '', so_lines))
            if so_lines:
                pass
                # raise ValidationError(_('The following products cannot be restricted to the company'
                #                         ' %s because they have already been used in quotations or '
                #                         'sales orders in another company:\n%s\n'
                #                         'You can archive these products and recreate them '
                #                         'with your company restriction instead, or leave them as '
                #                         'shared product.') % (target_company.name, ', '.join(used_products)))

    @api.depends('project_id')
    def compute_filter_privilege_id(self):
        for rec in self:
            rec.filter_privilege_id = rec.project_id.project_singularity_ids.mapped('privilege_id').ids


    def product_activity_notifications(self,users,res_id,summary):

        for user in users:
            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'user_id': user,
                'res_id': res_id,
                'type':'request',
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
    # def notify_onchange_state(self):
    #     for rec in self:
    #         users=[]
    #         for user in self.env.ref('archer_realestate_notification.group_operations').users:
    #             if user.id not in users:
    #                 users.append(user.id)
    #         for user in self.env.ref('archer_realestate_notification.group_ceo').users:
    #             if user.id not in users:
    #                 users.append(user.id)
    #         for user in self.env.ref('real_estate_security.group_manager').users:
    #             if user.id not in users:
    #                 users.append(user.id)
    #         if len(users) > 0:
    #             self.product_activity_notifications(users,rec.id,'Unit Status Changed')
    #             res_users = self.env['res.users'].search([('id', 'in', users)])
    #             print(res_users)
    #             for notify in res_users:
    #                 notify.notify_info(message=f'Unit {rec.name} Status {rec.state_value}', title='Unit Status', sticky=True,
    #                                    target=notify.partner_id)
    # states_chnges = fields.Char(compute='notify_status_change',store=True)
    # @api.depends('state')
    # def notify_status_change(self):
    #     for rec in self:
    #         rec.states_chnges = rec.state
    #         rec.notify_onchange_state()
    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            rec.unit_type_id= False
            rec.map_url= rec.project_id.map_url
            rec.payment_plan_id = rec.project_id.payment_plan_ids.ids
            if rec.is_composite:
                rec.composite_unit_ids = False
    def reset_payment_plan_id(self):
        for rec in self:
            rec.payment_plan_id = rec.project_id.payment_plan_ids


    @api.onchange('project_id')
    @api.constrains('project_id')
    def onchange_project_set_carspot(self):
        for rec in self:
            if not rec.is_composite:
                rec.car_spot = rec.project_id.car_spot
                rec.car_spot_price = rec.project_id.car_spot_price
                rec.parking_code = rec.project_id.parking_code

    @api.onchange('composite_unit_ids')
    def onchange_composite_unit_ids(self):
        for rec in self:
            rec.total_Area = sum(rec.composite_unit_ids.mapped('total_Area'))
            rec.list_price = sum(rec.composite_unit_ids.mapped('list_price'))
            print(rec.list_price)
            rec.min_deposit_amount = sum(rec.composite_unit_ids.mapped('min_deposit_amount'))
            rec.car_spot = any(f.car_spot for f in rec.composite_unit_ids)
            rec.car_spot_price = sum(rec.composite_unit_ids.mapped('car_spot_price'))


    _sql_constraints = [
        ("parking_code_unique", "unique(parking_code, project_id)", "Parking Code Unique per project")
    ]

    filter_privilege_id = fields.Many2many(comodel_name="privilege.privilege", compute="compute_filter_privilege_id" )
    unit_type_id = fields.Many2one(comodel_name="unit.type",string='Unit Type')
    unit_category_id = fields.Many2one(comodel_name="project.category",)
    attached_area_ids = fields.One2many(comodel_name="attached.area.line",inverse_name='product_id')
    total_attached_area = fields.Float(compute="compute_total_attached_area",store=True)
    total_utilities = fields.Float(compute="compute_total_utilities",store=True)
    car_spot = fields.Boolean(string="",)
    car_spot_price = fields.Float()
    maintenance_deposit = fields.Boolean(string='Utilities Delivery', track_visibility='onchange', )
    unit_deleivery = fields.Boolean(string='Unit Delivery', track_visibility='onchange', )
    building_deleivery = fields.Boolean(string='Building Delivery', track_visibility='onchange', )
    key_deleivery = fields.Boolean(string='Key Delivery', track_visibility='onchange', )
    electricity_deleivery = fields.Boolean(string='Electric Delivery', track_visibility='onchange', )
    planet = fields.Boolean(string='Planet Area', track_visibility='onchange', )
    planet_date = fields.Date(string="Date", required=False, )
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False,
                                          readonly=False,
                                          ondelete='cascade', store=True,
                                          help="Link this project to an analytic account if you need financial management on projects. "
                                               "It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    total_amout = fields.Float(compute='_compute_total_amount', store=True)
    remain_amount = fields.Float(string='Remaining Amount', compute='_compute_remain_amount')
    remain_amount_with_interest = fields.Float(string='Remaining Amount With Interest',
                                               compute='_compute_remain_amount_with_interest')
    booked_date = fields.Date(string='Booked Date')
    hold_date = fields.Date(string='Hold Date')
    image_ids = fields.One2many('product.image', 'product_id', string='Product Images')
    purchase_ok = fields.Boolean('Can be Purchased', default=False, track_visibility='onchange', )
    is_residential = fields.Boolean('Is Unit', default=False, track_visibility='onchange', )
    is_composite = fields.Boolean('Is Composite', default=False, track_visibility='onchange', )
    composite_unit_ids = fields.Many2many('product.template','product_tmpl_rel','ptid','cptid',string="Units")
    is_land = fields.Boolean('Is Land', default=False, track_visibility='onchange', )
    is_interest = fields.Boolean('Is Interest', default=False, track_visibility='onchange', )
    is_penalty = fields.Boolean('Is Penalty', default=False, track_visibility='onchange', )
    # payment_plan_id = fields.Many2one('payment.plan',
    #                                    track_visibility='onchange', string='Payment Plan')
    payment_plan_id = fields.Many2many('payment.plan', 'payment_table1', 'merge1', 'plan_table1',
                                       track_visibility='onchange', string='Payment Plan')
    product_room_ids = fields.One2many('product.room', 'product_id', track_visibility='onchange', )
    product_history_ids = fields.One2many('product.history', 'product_id', track_visibility='onchange', )
    product_utility_ids = fields.One2many('product.utility', 'product_id', track_visibility='onchange', )
    customer_id = fields.Many2one('res.partner', string='Property Customer', track_visibility='onchange', )
    vendor_id = fields.Many2one('res.partner', domain=[('supplier', '=', True)], string='Property Owner',
                                track_visibility='onchange', )
    unit_code = fields.Char(string='Unit Identifier', default='code', track_visibility='onchange', )
    requset_id = fields.Many2one('product.request')
    state = fields.Selection([
        ('sale', 'For Sale'),
        ('hold', 'Hold'),
        ('booked', 'Booked'),
        ('contract', 'Contract'),
        ('deal', 'Deal'),
        ('sold', 'Sold'),
        ('blocked', 'Blocked'),
        ('under_review', 'Under Review'),
    ], string='Status', readonly=False, copy=False, index=True, track_visibility='onchange', default='blocked')
    confirm_date = fields.Date(string='Confirmation Date', readonly=True)
    floor_num = fields.Integer(string='Floor # invisible')
    floor_number = fields.Integer(string='Floor # invisible', )
    room = fields.Integer(string='# Rooms', track_visibility='onchange', )
    total_Area = fields.Float(string='Unit Area', track_visibility='onchange', )
    min_deposit_amount = fields.Monetary(string="Min Deposit Amount", track_visibility='onchange', )
    min_deposit_amount_temp = fields.Monetary(string="Min Deposit Amount Temp")
    delivery_date = fields.Date(string='Delivery Date')
    actual_delivery_date = fields.Date(string='Actual Delivery Date')
    delivery_type = fields.Selection(selection=[('forced_delivery', 'Forced delivery'),
                                                ('actual_delivery', 'Actual delivery'), ])
    finishing_type_id = fields.Many2one(comodel_name="finishing.type", string="Finishing Type", )
    project_utility_ids = fields.Many2many('utility.utility', compute='calc_project_utilities_ids')
    reserve_days_no = fields.Integer(string="No. of Reservation Days ",compute="get_reserve_days_no",
                                     reverse="set_reserve_days_no",store=True)

    @api.depends('attached_area_ids','attached_area_ids.price')
    def compute_total_attached_area(self):
        for rec in self:
            total = 0
            for area in rec.attached_area_ids:
                total += area.total
            rec.total_attached_area = total

    @api.depends('product_utility_ids','price_before_discount','list_price')
    def compute_total_utilities(self):
        for rec in self:
            total = 0
            for utility in rec.product_utility_ids:
                total += utility.price
            rec.total_utilities = total

    @api.depends('project_id','project_id.reserve_days_no')
    def get_reserve_days_no(self):
        for rec in self:
            rec.reserve_days_no = rec.project_id.reserve_days_no

    @api.depends('project_id')
    def calc_project_utilities_ids(self):
        for rec in self:
            rec.project_utility_ids = rec.project_id.project_utility_ids.mapped('utility_id').ids


    def repeat_installments_creation(self):
        invoice_ids = self.env['account.move'].search([('unit_id', '=', self.id), ('state', '=', 'draft')])
        if invoice_ids:
            for invoice in invoice_ids:
                invoice_id = self.env['account.move'].create({
                    'sale_order': invoice.sale_order.id,
                    'unit_id': invoice.unit_id.id,
                    'partner_id': self.customer_id.id,
                    'analytic_account_id': invoice.analytic_account_id.id,
                    'account_id': self.customer_id.property_account_receivable_id.id,
                    'invoice_date_due': invoice.invoice_date_due,
                    'invoice_date': invoice.invoice_date_due,
                    'date_temp': invoice.invoice_date_due,
                    'move_type': 'out_invoice',
                    'state': 'draft',
                })
                account_id = ""
                if invoice.unit_id.id:
                    account_id = invoice.unit_id.property_account_income_id.id or invoice.unit_id.categ_id.property_account_income_categ_id.id
                if not account_id:
                    raise UserError(
                        _(
                            'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (invoice.unit_id.product_variant_id.name,))

                if invoice.unit_id.min_deposit_amount == 0:
                    raise UserError(
                        _(
                            'Please add Min Deposit Amount For Unit "%s"') %
                        (self.unit_id.name,))
                for line in invoice.invoice_line_ids:
                    invoice_line_ids = self.env['account.move.line'].create({
                        'name': str(invoice.name) + ' / ' + str(self.customer_id.name),
                        'move_id': invoice_id.id,
                        'account_id': account_id,
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'price_unit': line.price_unit,
                        'price_subtotal': line.price_subtotal,
                    })
                invoice.state = 'cancel'
                # invoice_id.action_invoice_open()
                # invoice.move_id.reverse_moves(date=datetime.datetime.now())
        self.state = 'sale'
        return {
            'name': "Offer",
            'context': {
                'default_unit_id': self.id,
                'default_partner_id': self.customer_id.id,
                'default_repeat_installements': True,
                'default_readonly': True
            },
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.constrains('name')
    def _edit_analytic_account_id_name(self):
        for pro in self:
            if pro.analytic_account_id:
                pro.analytic_account_id.name = pro.name

    @api.model
    def create(self, vals):
        product = super(ProductTemplateInherited, self).create(vals)
        product.check_val_of_product_utility_ids()
        # print("=================self.product_project.fee_percent",pro.product_project)
        if product.is_residential == True or product.is_land == True:
            analytic_account = self.env['account.analytic.account'].create({
                'name': str(product.name),
                'code': str(product.id),
                'is_project': False,
                'is_unit_property': True,
                'property_account_receivable_id': product.project_id.property_account_receivable_id,
                'company_id': product.company_id.id,
            })
            product.update({"analytic_account_id": analytic_account})
        return product

    @api.depends('remain_amount', 'analytic_account_id', 'is_interest')
    def _compute_remain_amount_with_interest(self):
        for prod in self:
            invoice_line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),
                                                                     ('product_id.product_tmpl_id.is_interest', '=',
                                                                      True),
                                                                     ('product_id', '=', prod.product_variant_id.id),
                                                                     ])
            total_price = 0.0
            if invoice_line_ids:
                for line in invoice_line_ids:
                    total_price = total_price + line.price_subtotal
            for prop in self:
                prop.remain_amount_with_interest = abs(total_price + prop.remain_amount)


    @api.depends('analytic_account_id')
    def _compute_remain_amount(self):
        for rec in self:
            if rec.analytic_account_id:
                invoices = self.env['account.move'].search([
                                                 ('utility_invoice','=',False)])
                total_remain = 0
                for inv in invoices:
                    total_remain += inv.amount_residual
                rec.remain_amount = total_remain
            else:
                rec.remain_amount = 0

    @api.depends('list_price', 'product_utility_ids', 'payment_plan_id')
    def _compute_total_amount(self):
        for product in self:
            product.total_amout = product.list_price
            for line in product.product_utility_ids:
                if line.included_price == True:
                    product.total_amout += line.price

    def action_view_hold_units(self):
        return {
            'name': "Hold Requests",
            'domain': [('product_id', '=', self.id)],
            'view_mode': 'list,form',
            'res_model': 'product.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_create_sale_order_inherited(self):
        return {
            'name': "Offer",
            'context': {
                'form_view_ref': 'real_estate.sale_order_view_tree_inherit_crm',
                'default_unit_id': self.id,
                'default_partner_id': self.customer_id.id,
                'default_readonly': True
            },
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_image_preview(self):
        images_ids = self.env['product.image'].search([('product_id', '=', self.id)])
        compose_form = self.env.ref('real_estate.real_image_preview_form')
        if not images_ids:
            raise ValidationError("There Is No Images To View")
        else:
            return {
                'name': 'Image Preview',
                'view_mode': 'form',
                'res_model': 'product.image.preview',
                'type': 'ir.actions.act_window',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': {
                    'default_product_id': self.id,
                    'default_image_id': images_ids[0].id,
                    'default_image_ids': [(6, 0, self.image_ids.ids)],
                    'default_image_preview': images_ids[0].image,
                },
                'target': 'current',
            }


    # @api.model
    # def automate_hold(self):
    #     yt = self.search([('state', '=', 'hold'), ('hold_date', '!=', False), ('is_residential', '=', True)])
    #     today = datetime.date.today()
    #     for product in yt:
    #         if today and product.hold_date:
    #             start_dt = fields.Datetime.from_string(product.hold_date)
    #             finish_dt = fields.Datetime.from_string(today)
    #             difference = relativedelta(finish_dt, start_dt)
    #             days = difference.days
    #             diff = round(days, 2)
    #             if product.requset_id.hold_type == 'automatic':
    #                 if diff >= product.requset_id.hold_days:
    #                     product.state = 'sale'
    #                     product.customer_id = False
    #                     product.hold_date = False
    #                     product.booked_date = False
    #                     if product.requset_id:
    #                         product.requset_id.active = False
    #                         product.requset_id = False
    #                     if product.analytic_account_id:
    #                         product.analytic_account_id.partner_id = False

    @api.onchange('is_residential', 'is_land')
    @api.constrains('is_residential', 'is_land')
    def _onchange_is_residential(self):
        for line in self:
            if line.is_residential == True or line.is_land == True:
                line.type = 'service'
                line.detailed_type = 'service'

    def action_hold_request(self):
        compose_form = self.env.ref('real_estate.sale_hold_request_wizard')
        return {
            'name': 'Hold Request',
            'view_mode': 'form',
            'res_model': 'product.request',
            'type': 'ir.actions.act_window',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'context': {
                'default_sales_person_id': self.env.user.id,
                'default_product_id': self.id,
            },
            'target': 'new',
        }

    def action_block_product(self):
        self.state = 'blocked'
        history_line_ids = self.env['product.history'].create({
            'product_id': self.id,
            'state': 'blocked',
            'confirm_date': datetime.datetime.now(),
        })

    def action_book_product(self):
        self.sudo().update({'state': 'booked'})
        history_line_ids = self.env['product.history'].create({
            'product_id': self.id,
            'state': 'booked',
            'confirm_date': datetime.datetime.now(),
        })

    def button_product_cede_form(self):
        compose_form = self.env.ref('real_estate.sale_product_cede_form')
        return {
            'name': 'Property',
            'view_mode': 'form',
            'res_model': 'product.cede',
            'type': 'ir.actions.act_window',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': {
                'default_product_id': self.id,
            },
        }

    def action_recovery_product(self):
        self.customer_id = False
        self.state = 'sale'
        self.hold_date = False
        self.booked_date = False
        if self.requset_id:
            self.requset_id.active = False
            self.requset_id = False
        if self.analytic_account_id:
            self.analytic_account_id.partner_id = False
        history_line_ids = self.env['product.history'].create({
            'product_id': self.id,
            'state': 'recovery',
            'confirm_date': datetime.datetime.now(),
        })

    def action_replace_product(self):
        self.customer_id = False
        self.state = 'sale'
        self.hold_date = False
        self.booked_date = False
        if self.requset_id:
            self.requset_id.active = False
            self.requset_id = False
        if self.analytic_account_id:
            self.analytic_account_id.partner_id = False
        history_line_ids = self.env['product.history'].create({
            'product_id': self.id,
            'state': 'replace',
            'confirm_date': datetime.datetime.now(),
        })

    def action_sold_product(self):
        self.state = 'sold'
        history_line_ids = self.env['product.history'].create({
            'product_id': self.id,
            'state': 'sold',
            'confirm_date': datetime.datetime.now(),
        })

    def action_back_to_sale_product(self):
        self.customer_id = False
        self.state = 'sale'
        self.hold_date = False
        self.booked_date = False
        if self.requset_id:
            self.requset_id.active = False
            self.requset_id = False
        if self.analytic_account_id:
            self.analytic_account_id.partner_id = False
        history_line_ids = self.env['product.history'].create({
            'product_id': self.id,
            'state': 'sale',
            'confirm_date': datetime.datetime.now(),
        })

    privilege_ids = fields.One2many(comodel_name="unit.privilege", inverse_name="product_id", string="Privileges",
                                    required=False, )
    singularity_ids = fields.Many2many(comodel_name="privilege.privilege", string="Available privilege",
                                       compute="calc_singularity_ids", store=True)
    meter_price = fields.Float('Price/Meter(Area)')
    land_meter_price = fields.Float('Price/Meter(Land)')
    land_area = fields.Float('Land Area')
    extra_land = fields.Float('Extra Land')
    extra_land_price = fields.Float('Price/Meter(Extra Land)')

    total_percent = fields.Float('Total Price', compute="compute_total_percent", store=True)
    meter_cash_percent = fields.Float('Price Per Meter', compute="compute_meter_cash_percent", store=True)

    building_license_no = fields.Char('Building License No.')
    parking_code = fields.Char('Parking Code')
    unit_design_ref = fields.Char('Unit Design Ref.')
    # coding fields
    product_areas = fields.Many2one('product.area',related="project_id.product_areas")
    product_building = fields.Many2one('product.building', track_visibility='onchange')
    product_project = fields.Many2one('account.analytic.account', track_visibility='onchange',related='project_id.analytic_account_id',store=True )
    project_id = fields.Many2one('real.estate.project', track_visibility='onchange',string='Project' )
    unit_type_ids = fields.Many2many("unit.type",'ut_rel','ut_id','pr_id',related='project_id.unit_type_ids',store=True,ondelete='cascade',string='Unit Types')

    building_code = fields.Many2one('project.building', string='Building Code')
    phase_no = fields.Many2one('project.phase', 'Phase No.')
    unit_classification = fields.Selection(selection=[('bank', 'Bank'),
                                                      ('rental', 'Rental'),
                                                      ('block', 'Block'),
                                                      ('timeshare', 'TimeShare'),
                                                      ('directors_board', 'Directors Board'),],)
    payment_plan_ids = fields.Many2many('payment.plan','payplan_pro_rel','papid','prodid',
                                        string="Payment Plans",
                                        compute="compute_payment_plans",
                                        store=True,ondelete='cascade' )
    apply_discount = fields.Boolean('Apply Discount')
    discount_type = fields.Selection([('amount', 'Amount'), ('percentage', 'Percentage')], default='amount',
                                     string='Discount')
    discount_amount = fields.Float('Amount')
    discount_percentage = fields.Float('Percentage')
    price_before_discount = fields.Float('Price Before Discount')
    price_disc = fields.Float('Discount Amount',compute='get_disc_amount',store=True)
    @api.depends('price_before_discount','discount_amount','list_price')
    def get_disc_amount(self):
        for rec in self:
            amount = 0
            if rec.apply_discount:
                amount = rec.price_before_discount - rec.list_price
            rec.price_disc = amount

    # @api.onchange('payment_plan_id','apply_discount')
    # def onchange_payment_plan_id(self):
    #     for rec in self:
    #         if rec.payment_plan_id and rec.apply_discount:
    #             rec.discount_type = rec.payment_plan_id.discount_type
    #             rec.discount_amount = rec.payment_plan_id.discount_amount
    #             rec.discount_percentage = rec.payment_plan_id.discount_percentage
    #         else:
    #             rec.discount_amount = 0
    #             rec.discount_percentage = 0

    @api.depends('phase_no','is_composite','composite_unit_ids')
    def compute_payment_plans(self):
        for rec in self:
            if rec.is_composite:
                rec.payment_plan_ids = rec.composite_unit_ids.mapped('payment_plan_id').ids
            else:
                rec.payment_plan_ids = rec.phase_no.payment_plan_ids.ids


    docs_ids = fields.Many2many('ir.attachment', 'product_attach_rel','product_id','attach_id', string='Other Materials')
    map_url = fields.Char('Map URL')

    floor = fields.Many2one('building.floor', string='Floor #', track_visibility='onchange', )

    num_temp = fields.Char(string="Name tmp")
    name = fields.Char('Name', default='New', index=True, required=True)
    project_unit_cost = fields.Float('Unit Cost', help="This cost = cost of meter on project * unit area")
    move_ids = fields.Many2many('account.move', string='Moves')
    unit_costing = fields.Boolean('Unit Costing')

    @api.depends('privilege_ids.privilege_id','privilege_ids')
    def calc_singularity_ids(self):
        for rec in self:
            rec.singularity_ids = rec.privilege_ids.mapped('privilege_id').ids

    @api.depends('privilege_ids', 'privilege_ids.percent')
    def compute_total_percent(self):
        for rec in self:
            rec.total_percent = sum(rec.privilege_ids.mapped('percent'))

    @api.depends('total_percent', 'meter_price')
    def compute_meter_cash_percent(self):
        for rec in self:
            rec.meter_cash_percent = rec.meter_price + (rec.total_percent / 100 * rec.meter_price)


    update_unit_prices = fields.Char(compute="onchange_listprice",store=True)
    @api.depends('total_Area', 'meter_price', 'total_attached_area',
                  'car_spot_price', 'meter_price','apply_discount','discount_type',
                  'discount_amount','discount_percentage')
    def onchange_listprice(self):
        for rec in self:
            if not rec.is_composite:
                price = (rec.meter_price * rec.total_Area) + rec.total_attached_area + rec.car_spot_price
                if rec.apply_discount:
                    if rec.discount_type =='amount':
                        price_after_disc = price - rec.discount_amount
                    else:
                        price_after_disc = price - (rec.discount_percentage/100*price)
                    rec.list_price = price_after_disc
                    rec.price_before_discount = price
                else:
                    rec.price_before_discount = rec.list_price = price
            rec.update_unit_prices = rec.update_unit_prices

    @api.constrains('privilege_ids', 'privilege_ids.percent')
    def _check_percent(self):
        for x in self:
            for rec in x.privilege_ids:
                if rec.percent < 0.0:
                    raise exceptions.ValidationError('Percent Must Be >= 0')
                
                elif rec.percent >= 100:
                    raise exceptions.ValidationError('Percent Must Be < 100')
            if sum(x.mapped('total_percent')) > 100:
                raise exceptions.ValidationError('Total Percent Must Be <= 100')
            priv_list = [rec.privilege_id.prev_id.name for rec in x.privilege_ids]
            priv_list = list(set(priv_list))
            if len(x.privilege_ids) > len(priv_list):
                raise exceptions.ValidationError("Singularities can't be repeated")

    def check_val_of_product_utility_ids(self):
        if not self.product_utility_ids and self.is_residential:
            pass
            # raise exceptions.ValidationError(_('You Must Select Utility !!'))

    @api.constrains('product_utility_ids')
    def _check_product_utility_ids(self):
        for rec in self:
            if not rec.product_utility_ids:
                pass
                # raise exceptions.ValidationError(_('You Must Select Utility !!'))
            util_list = [x.name.name for x in rec.product_utility_ids]
            util_list = list(set(util_list))
            if len(rec.product_utility_ids) > len(util_list):
                raise exceptions.ValidationError("Utilities can't be repeated")
    def action_receive_unit(self):
        self.unit_deleivery = True

    def create_accounting_entry(self):
        xx = self.env.context.get('active_domain')
        if not xx:
            raise exceptions.ValidationError('You Can deliver unit only from project form ')
        for rec in self.filtered(lambda x: not x.move_ids):
            moves = self.env['account.move']
            moves |= rec.create_reconcile_move()
            moves |= rec.create_cost_move()
            moves |= rec.create_inventory_move()
            rec.move_ids = moves
            rec.unit_deleivery = True

    def create_reconcile_move(self):
        journal_id = self.project_id.journal_id
        credit_account_id = self.project_id.credit_account_id
        income_account_id = self.categ_id.property_account_income_categ_id.id
        if not income_account_id:
            raise exceptions.ValidationError("You Must Define Income Account on  Category Unit")

        self.check_accounting_info(journal_id, credit_account_id, income_account_id)
        sale_obj = self.env['sale.order'].search([('unit_id', '=', self.id), ('state', '=', 'sale')])
        sale_obj = sale_obj.sorted(lambda key: key.create_date)
        sale_obj = sale_obj[0] if sale_obj else sale_obj
        invoices = self.env['account.move'].sudo().search([
            ('partner_id', '=', sale_obj.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('sale_order', '=', sale_obj.id),
        ])
        ref = 'Reconciled Entry on Unit {}'.format(self.name)
        total_invoices = sum(invoices.mapped('amount_total'))
        if total_invoices:
            move_vals = self.prepare_reconceil_move_vals(ref, sale_obj.partner_id.id, int(credit_account_id),
                                                         income_account_id, int(journal_id), total_invoices)
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            return move
        else:
            return self.env['account.move']

    def create_inventory_move(self):
        journal_id = self.project_id.cost_journal_id.id
        credit_account_id = self.project_id.cost_debit_account_id.id
        debit_account_id = self.project_id.property_stock_valuation_account_id
        if not journal_id:
            raise exceptions.ValidationError('Please Set Stock Journal On Unit Category !')
        if not debit_account_id:
            raise exceptions.ValidationError('Please Set Income Account On Unit Category !')

        self.check_accounting_info(journal_id, credit_account_id, debit_account_id)

        ref = 'Inventory Entry on Unit {}'.format(self.name)

        if self.project_unit_cost:
            move_vals = self.prepare_reconceil_move_vals(ref, self.customer_id.id, int(credit_account_id),
                                                         int(debit_account_id), int(journal_id), self.project_unit_cost)
            _logger.info("move_vals:{}".format(move_vals))
            for value in move_vals.get('line_ids'):
                value[2].update({'analytic_account_id': self.product_project.id})
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            return move
        else:
            return self.env['account.move']

    mv = fields.Many2many('account.move', 'account_mv_rel', 'd_id', 'g_id')

    def create_cost_move(self):
        if self.project_id:
            journal_id = self.project_id.cost_journal_id
            # if self.product_project.is_delivered:
            debit_account_id = self.project_id.cost_credit_account_id
            credit_account_id = self.project_id.property_stock_valuation_account_id

            self.check_accounting_info(journal_id, credit_account_id, debit_account_id)

            aml_objs = self.env['account.move.line'].search([
                ('move_id.is_unit_cost', '=', False),
                ('move_id.state', '=', 'posted'),
                ('move_id.is_cost_entry', '=', False),
                ('analytic_account_id', '=', self.product_project.id),
                ('account_id.is_costing', '=', True),
            ])
            moves = aml_objs.mapped('move_id')
            total_cost = sum(moves.mapped('amount_total'))
            # units = self.search([('product_project', '=', self.product_project.id), ('unit_costing', '=', True)])
            # total_area = sum(units.mapped('total_Area'))
            # total_area += sum(units.mapped('land_area'))
            # total_area += sum(units.mapped('extra_land'))
            total_area = self.project_id.total_meter
            if not total_area:
                raise exceptions.ValidationError(
                    'Total Area Of project Units Must Be >0 Or there is no units has Unit costing')
            meter_cost = total_cost / total_area
            self.mv = moves
            _logger.info('moves {}'.format(moves))
            _logger.info('Total Area {}'.format(total_area))
            _logger.info('meter Cost{}'.format(meter_cost))
            _logger.info('total cost {}'.format(total_cost))
            ref = 'Cost Of Unit {} on Project {}'.format(self.name, self.project_id.name)
            self.project_unit_cost = meter_cost * (self.total_Area + self.land_area + self.extra_land)
            vl = meter_cost * (self.total_Area + self.land_area + self.extra_land)
            move_vals = self.prepare_reconceil_move_vals(ref, self.customer_id.id, int(credit_account_id),
                                                         int(debit_account_id), int(journal_id), vl, check1=True)
            if vl:

                move = self.env['account.move'].create(move_vals)

                move.action_post()
                return move
            else:
                return self.env['account.move']
        else:
            return self.env['account.move']

    def prepare_reconceil_move_vals(self, ref, partner, credit_account, debit_account, journal, amount, check1=False):
        move = {
            'date': fields.date.today(),
            'type': 'entry',
            'ref': ref,
            'is_unit_cost': True if check1 else False,
            'is_cost_entry': True,
            'journal_id': journal,
            'company_id': self.env.user.company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': debit_account,
                    'partner_id': partner,
                    'analytic_account_id': self.analytic_account_id.id if check1 else False,
                    'debit': amount,
                    'credit': 0}),
                (0, 0, {
                    'account_id': credit_account,
                    'partner_id': partner,
                    'debit': 0,
                    'analytic_account_id': self.product_project.id if check1 else False,

                    'credit': amount})]
        }
        return move

    def check_accounting_info(self, journal_id, credit_account_id, debit_account_id=False):
        lost = ''
        if not journal_id:
            lost += 'Journal'
        if not credit_account_id:
            lost += ',Credit Account'
        if not debit_account_id:
            lost += ',Debit Account'
        if lost:
            raise exceptions.ValidationError(
                "You Must Define {} in Project or Check Stock Valuation Account on Unit Category".format(lost))

    def action_view_entry(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('id', 'in', self.move_ids.ids)]
        }
    def convert_to_available(self):

        for rec in self.filtered(lambda x:x.state in ['blocked','under_review']):
            rec.state = 'sale'
    attached_area_frist = fields.Char('Attached Area',compute='compute_attached_area_frist')
    attached_area_frist_price = fields.Float('Attached area price',compute='compute_attached_area_frist',store=True)

    @api.depends('attached_area_ids')
    def compute_attached_area_frist(self):
        for rec in self:
            attach = 0
            price = 0
            if rec.attached_area_ids:
                for record in rec.attached_area_ids:
                    attach = record.area
                    price = record.price
            rec.attached_area_frist = attach
            rec.attached_area_frist_price = price

