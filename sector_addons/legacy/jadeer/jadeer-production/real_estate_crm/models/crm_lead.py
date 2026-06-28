# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from lxml import etree
from bs4 import BeautifulSoup
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, tools, SUPERUSER_ID


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    local_overseas = fields.Selection(string="Local/Overseas", selection=[('local', 'Local'),
                                                                          ('overseas', 'Overseas'), ], required=False, )
    source = fields.Selection(string="Source", selection=[('direct', 'Direct'),
                                                          ('indirect', 'Indirect'),('personal','Personal'),('ambassador','Ambassador'), ], required=False,)
    log_notes = fields.Char(string="Notes", compute="compute_log_note")
    log_date = fields.Date('Note Date', compute="compute_log_note")
    # user_id = fields.Many2one('res.users',default=False)
    # team_id = fields.Many2one('crm.team',default=False)

    @api.depends('message_ids')
    def compute_log_note(self):
        for rec in self:
            log_notes = ''
            log_date = False
            mails = self.env['mail.message'].search([('res_id', '=', rec.id), ('model', '=', 'crm.lead'),
                                                     ('body', 'not in', ['', False])], order="id desc", limit=1)
            if mails and mails.body:
                soup = BeautifulSoup(mails.body, features='lxml')
                log_notes += soup.get_text()
                log_date = mails.write_date.date()
            else:
                mails = self.env['mail.activity'].search([('res_id', '=', rec.id), ('res_model', '=', 'crm.lead'),
                                                          ('note', '!=', False)], order="id desc", limit=1)
                if mails and mails.note:
                    soup = BeautifulSoup(mails.note, features='lxml')
                    log_notes += soup.get_text()
                    log_date = mails.write_date.date()
            rec.log_date = log_date
            rec.log_notes = log_notes


    def action_new_quotation(self):
        action = self.env.ref("real_estate.action_offers_new").read()[0]
        action['context'] = {
            'form_view_ref':'real_estate.sale_order_view_tree_inherit_crm',
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'default_unit_id': self.unit_id.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_team_id': self.team_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_user_id': self.user_id.id if self.user_id else False,
            'default_sale_person2_id': self.sale_person2_id.id if self.sale_person2_id else False,
            'default_sale_person3_id': self.sale_person3_id.id if self.sale_person3_id else False,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': self.tag_ids.ids,
            'default_broker_id': self.broker_id.id,
            'default_broker_manager_id': self.broker_manager_id.id,
            'default_broker_sales_id': self.broker_sales_id.id,
            'default_local_overseas': self.local_overseas,
            'default_source': self.source,
        }
        return action

    def action_sale_quotations_new(self):
        return super(CRMLead, self.with_context(create=True)).action_sale_quotations_new()

    def action_view_sale_quotation(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        ctx = self.env.context.copy()
        ctx.update({
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
            'form_view_ref':'real_estate.sale_order_view_tree_inherit_crm',
            'tree_view_ref':'real_estate.sale_order_view_tree2'
        })
        domain = [('opportunity_id', '=', self.id), ('state', 'not in', ['sale', 'down_payment'])]

        action = {
            'name': _('Offers'),
            'view_mode': 'tree,form,search',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain,
            'target': 'current'
        }
        return action

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders').read()[0]
        ctx = self.env.context.copy()
        ctx.update({
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
            'form_view_ref': 'real_estate.sale_order_view_tree_inherit_crm',
            'tree_view_ref': 'real_estate.sale_order_view_tree2'
        })
        domain = [('opportunity_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]

        action = {
            'name': _('Contracts'),
            'view_mode': 'tree,form,search',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain,
            'target': 'current'
        }
        return action
        return action

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CRMLead, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        create = self.env.user.has_group('real_estate_crm.group_leads_create')
        edit = self.env.user.has_group('real_estate_crm.group_leads_edit')
        doc = etree.XML(res['arch'])
        if doc :
            if create:
                if view_type == 'tree':
                    nodes = doc.xpath("//tree")
                    for node in nodes:
                        node.set('create', '1')

                    res['arch'] = etree.tostring(doc)
                elif view_type == 'form':
                    nodes = doc.xpath("//form")
                    for node in nodes:
                        node.set('create', '1')

                    res['arch'] = etree.tostring(doc)
                elif view_type == 'kanban':
                    nodes = doc.xpath("//kanban")
                    for node in nodes:
                        node.set('create', '1')

                    res['arch'] = etree.tostring(doc)
            else:
                if view_type in ['tree', 'form', 'kanban']:
                    nodes_tree = doc.xpath("//tree")
                    for node in nodes_tree:
                        node.set('create', '0')

                        print(node)
                    nodes_form = doc.xpath("//form")
                    for node in nodes_form:
                        node.set('create', '0')

                        print(node)
                    nodes_form = doc.xpath("//kanban")
                    for node in nodes_form:
                        node.set('create', '0')

                        print(node)
                    res['arch'] = etree.tostring(doc)
            if edit:
                if view_type == 'tree':
                    nodes = doc.xpath("//tree")
                    for node in nodes:
                        node.set('edit', '1')

                    res['arch'] = etree.tostring(doc)
                elif view_type == 'form':
                    nodes = doc.xpath("//form")
                    for node in nodes:
                        node.set('edit', '1')

                    res['arch'] = etree.tostring(doc)
                elif view_type == 'kanban':
                    nodes = doc.xpath("//kanban")
                    for node in nodes:
                        node.set('edit', '1')

                    res['arch'] = etree.tostring(doc)
            else:
                if view_type in ['tree', 'form', 'kanban']:
                    nodes_tree = doc.xpath("//tree")
                    for node in nodes_tree:
                        node.set('edit', '0')

                        print(node)
                    nodes_form = doc.xpath("//form")
                    for node in nodes_form:
                        node.set('edit', '0')

                        print(node)
                    nodes_form = doc.xpath("//kanban")
                    for node in nodes_form:
                        node.set('edit', '0')

                        print(node)
                    res['arch'] = etree.tostring(doc)


        return res
    unit_type = fields.Selection(
        string="Unit Type",
        selection=[
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
            ('medical', 'Medical'),
            ('administrative', 'Administrative'),
        ],
        required=False, default='residential')

    unit_type_id = fields.Many2one(comodel_name="unit.type",)
    unit_type_ids = fields.Many2many("unit.type",'unittype_rel','unittypeid','lead_id','Unit Types')

    project_id = fields.Many2one(comodel_name="real.estate.project", string="Project",)
    optional_project_id = fields.Many2one(comodel_name="real.estate.project", string="Optional Project",)
    unit_id = fields.Many2one(comodel_name="product.template", string="Unit",domain="[('state','=','sale')]")
    singularity_ids = fields.Many2many(comodel_name="privilege.privilege", string="Singularities", )
    filter_singularity_ids = fields.Many2many(comodel_name="privilege.privilege", string="Singularities",
                                              compute="compute_filter_singularity_ids")
    filter_unit_type_ids = fields.Many2many(comodel_name="unit.type", string="Unit Types",
                                              compute="compute_filter_unit_types_ids")
    price_min = fields.Monetary(string="Price Min", currency_field='company_currency', required=False, )
    price_max = fields.Monetary(string="Price Max", currency_field='company_currency', required=False, )

    area_min = fields.Float(string="Area Min", required=False, )
    area_max = fields.Float(string="Area Max", required=False, )

    floor_min = fields.Integer(string="Floor Min", required=False, )
    floor_max = fields.Integer(string="Floor Max", required=False, )

    room_min = fields.Integer(string="Floor Min", required=False, )
    room_max = fields.Integer(string="Floor Max", required=False, )
    age = fields.Char(string="Age",)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status',default='single',)
    industry_id = fields.Many2one('res.partner.industry', 'Industry')
    sale_person2_id = fields.Many2one(comodel_name="res.users", string="Salesperson 2",)
    sales_person2_id = fields.Many2one(comodel_name="res.users", string="Salesperson 2",)
    sales_person2_sale_team = fields.Many2one(comodel_name="crm.team", string="Sales Team 2",index=True,
        compute='_compute_team_id_2', readonly=False, store=True)
    sale_person3_id = fields.Many2one(comodel_name="res.users", string="Salesperson 3",)
    sales_person3_id = fields.Many2one(comodel_name="res.users", string="Salesperson 3",)
    sales_person3_sale_team = fields.Many2one(comodel_name="crm.team", string="Sales Team 3",index=True,
        compute='_compute_team_id_3', readonly=False, store=True)




    unit_state = fields.Selection([
        ('sale', 'For Sale'),
        ('hold', 'Hold'),
        ('booked', 'Booked'),
        ('contract', 'Contract'),
        ('deal', 'Deal'),
        ('sold', 'Sold'),
        ('blocked', 'Blocked'),
        ('under_review', 'Under Review'),
    ], string='unit Status', readonly=True, copy=False, store=True,compute='get_changed_unit_id')

    @api.depends('unit_id','unit_id.state')
    def get_changed_unit_id(self):
        for rec in self:
            state = False
            if rec.unit_id:
                state = rec.unit_id.state
            rec.unit_state = state

    @api.depends('sales_person2_id', 'type')
    def _compute_team_id_2(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for lead in self:
            # setting user as void should not trigger a new team computation
            if not lead.sales_person2_id:
                continue
            user = lead.sales_person2_id
            if lead.sales_person2_sale_team and user in (lead.sales_person2_sale_team.member_ids | lead.sales_person2_sale_team.user_id):
                continue
            team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
            team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=team_domain)
            lead.sales_person2_sale_team = team.id
    @api.depends('sales_person3_id', 'type')
    def _compute_team_id_3(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for lead in self:
            # setting user as void should not trigger a new team computation
            if not lead.sales_person3_id:
                continue
            user = lead.sales_person3_id
            if lead.sales_person3_sale_team and user in (lead.sales_person3_sale_team.member_ids | lead.sales_person3_sale_team.user_id):
                continue
            team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
            team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=team_domain)
            lead.sales_person3_sale_team = team.id

    @api.depends('project_id','optional_project_id')
    def compute_filter_unit_types_ids (self):
        for rec in self:
            projects = rec.project_id+rec.optional_project_id
            if projects:
                rec.filter_unit_type_ids = projects.mapped('unit_type_ids')
            else:
                rec.filter_unit_type_ids = False

    @api.depends('project_id','optional_project_id')
    def compute_filter_singularity_ids(self):
        for rec in self:
            projects = rec.project_id+rec.optional_project_id

            if projects:
                rec.filter_singularity_ids = projects.mapped('project_singularity_ids').mapped('privilege_id').ids
            else:
                rec.filter_singularity_ids = False



    @api.onchange('unit_type')
    def onchange_unit_type(self):
        if self.unit_type != 'residential':
            self.singularity_ids = False
            self.area_min = 0
            self.area_max = 0
            self.floor_min = 0
            self.room_min = 0
            self.room_max = 0
    def prepare_unit_search_domain(self):
        domain = [
            ('is_residential', '=', True),
            ('state', '=', 'sale'),
        ]
        # if self.unit_type:
        #     domain.append(
        #         ('unit_type', '=', self.unit_type)
        #     )
        if self.unit_type_ids:
            domain.append(
                ('unit_type_id', 'in', self.unit_type_ids.ids)
            )
        projects = self.project_id + self.optional_project_id

        if projects:
            domain.append(
                ('project_id', 'in', projects.ids)
            )
        if self.price_min:
            domain.append(
                ('list_price', '>=', self.price_min)
            )
        if self.price_max:
            domain.append(
                ('list_price', '<=', self.price_max)
            )
        if self.area_min:
            domain.append(
                ('total_Area', '>=', self.area_min)
            )
        if self.area_max:
            domain.append(
                ('total_Area', '<=', self.area_max)
            )
        if self.floor_min:
            domain.append(
                ('floor.code', '>=', self.floor_min)
            )
        if self.floor_max:
            domain.append(
                ('floor.code', '<=', self.floor_max)
            )
        if self.room_min:
            domain.append(
                ('room', '>=', self.room_min)
            )
        if self.room_max:
            domain.append(
                ('room', '<=', self.room_max)
            )
        return domain
    def prepare_compo_unit_search_domain(self):
        domain = [
            ('is_residential', '=', True),('is_composite','=',True),('state', '=', 'sale'),
        ]
        # if self.unit_type:
        #     domain.append(
        #         ('unit_type', '=', self.unit_type)
        #     )

        if self.project_id:
            domain.append(
                ('project_id', '=', self.project_id.id)
            )
        if self.price_min:
            domain.append(
                ('list_price', '>=', self.price_min)
            )
        if self.price_max:
            domain.append(
                ('list_price', '<=', self.price_max)
            )
        if self.area_min:
            domain.append(
                ('total_Area', '>=', self.area_min)
            )
        if self.area_max:
            domain.append(
                ('total_Area', '<=', self.area_max)
            )

        return domain

    def action_unit_search(self):
        domain = self.prepare_unit_search_domain()
        composite_domain = self.prepare_compo_unit_search_domain()
        res = self.env['product.template'].search(domain)
        composite_res = self.env['product.template'].search(composite_domain)
        if self.singularity_ids and res:
            res = res.filtered(
                lambda l: self.singularity_ids in l.singularity_ids or self.singularity_ids == l.singularity_ids)
        res |=composite_res
        if not res:
            raise exceptions.ValidationError('There is no unit matched with this search criteria !')
        view_ref = self.env.ref('real_estate_crm.select_unit_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'select.unit.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_ref,
            'target': 'new',
            'nodestroy': True,
            'context':{
                'default_lead_id': self.id
            }
        }
        # return action

    @api.constrains('stage_id','stage_id.is_won')
    def access_won_stage(self):
        if self.stage_id.is_won and not self.env.user.has_group('real_estate_crm.won_opportunity_access_group') and not self.env.context.get('offer'):
            raise ValidationError("Please Check Won Access for this Opportunity!")

    from_existing_partner = fields.Boolean()
    @api.constrains('mobile')
    def check_mobile_exist(self):
        if not self.from_existing_partner:
            unq_list = []
            res = self.env['crm.lead'].search([('id', '!=', self.id)])
            for rec in res:
                if rec.mobile:
                    mobile = rec.mobile.replace(" ", "")
                    if mobile.startswith('+2'):
                        mobile = mobile[2:]
                        unq_list.append(mobile)
                    else:
                        unq_list.append(rec.mobile)

            for record in self:
                if record.mobile:

                    value = record.mobile.replace(" ", "")
                    if value.startswith('+2'):
                        value = value[2:]
                    if value not in unq_list:
                        pass
                    else:
                        raise ValidationError("One of the Mobile Number already exist")
    @api.constrains('mobile')
    def check_mobile_size(self):
        for rec in self:
            if rec.mobile:
                mobile = str(rec.mobile).replace(" ", "")
                if mobile.startswith('+2'):
                    mobile = mobile[2:]
                if len(mobile) < 11:
                    raise ValidationError("Mobile Phone should  be 11 digit")
                elif len(mobile) > 11:
                    raise ValidationError("Mobile Phone should  be 11 digit")
                else:
                    pass


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_person2_id = fields.Many2one(related='opportunity_id.sales_person2_id',string="Salesperson 2",store=True)
    sale_person2_sale_team = fields.Many2one(related='opportunity_id.sales_person2_sale_team',string="Sales Team 2",store=True)
    sale_person3_id = fields.Many2one(related='opportunity_id.sales_person3_id',string="Salesperson 3",store=True)
    sale_person3_sale_team = fields.Many2one(related='opportunity_id.sales_person3_sale_team',string="Sales Team 3",store=True)
