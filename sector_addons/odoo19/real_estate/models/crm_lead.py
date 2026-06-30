# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta,date
from odoo import api, fields, models, tools, SUPERUSER_ID

import json
from lxml import etree
class ResCompany(models.Model):
    _inherit = 'res.company'

    crm_last_limited_time = fields.Float(string='Limited Time')
    crm_stage_ids = fields.Many2one('crm.stage','Crm Stage')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_last_limited_time = fields.Float(related='company_id.crm_last_limited_time',readonly=False,string='Limited Time')
    crm_stage_ids = fields.Many2one(related='company_id.crm_stage_ids',string='Crm Stage',readonly=False)


class Source(models.Model):
    _inherit = "utm.source"

    @api.constrains('name')
    def _check_uniques_source(self):
        for rec in self:
            if rec.name:
                res = self.search([('name', '=', rec.name), ('id', '!=', rec.id)])
                if res:
                    raise ValidationError('Source Name is unique!')
    exception = fields.Boolean(help='Any opportunity has this source will be ignored when unassgin opportunities that donnot have activity')


class CrmLeadInherited(models.Model):
    _inherit = "crm.lead"

    source_id = fields.Many2one(track_visibility='onchange')
    convert_opp_reason = fields.Char(string="Convert Opp Reason")
    broker_id = fields.Many2one('res.partner',string="Broker",)
    broker_manager_id = fields.Many2one('res.partner',string="Broker manager")
    broker_sales_id = fields.Many2one('res.partner',string="Broker Sales")

    converted_to_opp = fields.Boolean()

    CloseDateState = fields.Boolean(compute="leadCloseDateState")
    change_user_id = fields.Boolean(store=True)
    is_booked_unit = fields.Boolean(compute="get_booked_unit")
    partner_international_id = fields.Char(string='International number')
    partner_national_id = fields.Char(string='National id/passport')

    @api.constrains('partner_international_id')
    def check_partner_international_id_exist(self):
        unq_list = []
        res = self.env['crm.lead'].search([('id', '!=', self.id)])
        for rec in res:
            if rec.partner_international_id:
                partner_international_id = rec.partner_international_id.replace(" ", "")
                if partner_international_id.startswith('+2'):
                    partner_international_id = partner_international_id[2:]
                    unq_list.append(partner_international_id)
                else:
                    unq_list.append(rec.partner_international_id)

        for record in self:
            if record.partner_international_id:

                value = record.partner_international_id.replace(" ", "")
                if value.startswith('+2'):
                    value = value[2:]
                if value not in unq_list:
                    pass
                else:
                    raise ValidationError("International number already exist")
    @api.constrains('partner_international_id')
    def check_partner_international_id_size(self):
        for rec in self:
            if rec.partner_international_id:
                partner_international_id = str(rec.partner_international_id).replace(" ", "")
                if partner_international_id.startswith('+2'):
                    partner_international_id = partner_international_id[2:]
                if len(partner_international_id) < 13:
                    raise ValidationError("International number  should  more than 13 digit")
                else:
                    pass
    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        """ Extract data from lead to create a partner.

        :param name : furtur name of the partner
        :param is_company : True if the partner is a company
        :param parent_id : id of the parent partner (False if no parent)

        :return: dictionary of values to give at res_partner.create()
        """
        super(CrmLeadInherited, self)._prepare_customer_values(partner_name, is_company, parent_id)
        email_parts = tools.email_split(self.email_from)
        res = {
            'name': partner_name,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'comment': self.description,
            'team_id': self.team_id.id,
            'parent_id': parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': email_parts[0] if email_parts else False,
            'title': self.title.id,
            'function': self.function,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            'is_company': is_company,
            'type': 'contact',
            'partner_international_id':self.partner_international_id,
            'partner_national_id':self.partner_national_id

        }
        if self.lang_id:
            res['lang'] = self.lang_id.code
        return res

    def notify_sales_persons(self):
        # self.user_id.notify_info(message='Assigned Lead',sticky=True,title=self.name)

        self.activity_schedule(act_type_xmlid='crm.call_for_demo', user_id=self.env.uid, date_deadline=fields.Date.today())

    def get_booked_unit(self):
        for rec in self:
            if rec.unit_id.state == 'booked':
                rec.is_booked_unit = True
            else:
                rec.is_booked_unit = False
    def leadCloseDateState(self):
        for rec in self:
            stage = self.env.company.crm_stage_ids
            activity_time = self.env.company.crm_last_limited_time
            if rec.create_date:
                close = datetime.strptime(str(rec.create_date), "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=2+activity_time)
                now = datetime.now() + timedelta(hours=2)
                mail = self.env['mail.message'].search([('model','=','crm.lead'),('res_id','=',rec.id),('mail_activity_type_id','!=',False)])
                activity = self.env['mail.activity'].search([('res_model','=','crm.lead'),('res_id','=',rec.id)])
                # d = rec.close_date - timedelta(days=5)
                if close <= now:
                    rec.CloseDateState = True
                    if not rec.change_user_id and not mail and not activity:
                        rec.stage_id = stage.id
                        rec.user_id = False
                        rec.change_user_id = True
                else:
                    rec.CloseDateState = False
            else:
                rec.CloseDateState = False

    def write(self, vals):
        if 'active' in vals and not self.env.context.get('default_type') and not self.env.context.get('active_model'):
            if not self.env.user.has_group('crm_security.group_sale_manager') and not self.env.user.has_group('sales_team.group_sale_manager'):
                raise ValidationError('You are not allowed to archive,Only sales manager and crm admin can do')
        super(CrmLeadInherited, self).write(vals)
        return True
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(CrmLeadInherited, self).fields_view_get(view_id, view_type, toolbar=toolbar,
    #                                                               submenu=False)
    #     doc = etree.XML(res['arch'])
    #     fields = res.get('fields')
    #     if self.converted_to_opp:
    #         if view_type in ['form']:
    #             for field in fields:
    #                 for node in doc.xpath("//field[@name='%s']" % field):
    #                     modifiers = json.loads(node.get("modifiers"))
    #                     modifiers['readonly'] = True
    #                     node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc)
    #     return res
    #     return res
    def action_create_sale_order_inherited(self):
        self.ensure_one()
        return {
            'name': ('Offer Plan'),
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_team_id': self.team_id.id,
                'default_campaign_id': self.campaign_id.id,
                'default_medium_id': self.medium_id.id,
                'default_source_id': self.source_id.id,
                'default_crm_id': self.id,
                'default_broker_id': self.broker_id.id,
                'default_broker_manager_id': self.broker_manager_id.id,
                'default_broker_sales_id': self.broker_sales_id.id,
                'default_local_overseas': self.local_overseas,
                'default_source': self.source,
                'default_state': 'draft',
            },
            'target': 'current',
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmLeadInherited, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        sp_tl = self.env.user.has_group('crm_security.group_sale_person') or self.env.user.has_group('crm_security.group_sale_tl')
        sm = self.env.user.has_group('crm_security.group_sale_manager')
        sm_cm = self.env.user.has_group('sales_team.group_sale_manager') or self.env.user.has_group('crm_security.group_sale_manager')
        cm = self.env.user.has_group('sales_team.group_sale_manager')
        sysadmin_cm = self.env.user.has_group('sales_team.group_sale_manager') or self.env.user.has_group('base.group_system')
        doc = etree.XML(res['arch'])
        if sp_tl:
            if view_type in ['form', 'tree','kanban']:
                for node in doc.xpath("//field"):
                    # if node.attrib.get('name') in ['user_id', 'team_id']:
                    if node.attrib.get('name') not in ['description','stage_id','project_id', 'unit_type_ids','price_min','price_max','area_min','area_max','floor_min','floor_max','room_min','room_max',]:
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['readonly'] = True
                        modifiers['force_save'] = True
                        node.set("modifiers", json.dumps(modifiers))

                toolbar = res.get('toolbar')
                if toolbar:
                    actions = toolbar.get('action')
                    new_action = []
                    res.get('toolbar').update({'action': new_action})
                res['arch'] = etree.tostring(doc)
        if not sysadmin_cm:
            if view_type in ['form', 'tree','kanban']:
                if view_type == 'tree':
                    nodes_tree = doc.xpath("//tree")
                    for node in nodes_tree:
                            node.set('delete', '0')
                elif view_type == 'form':
                    nodes_tree = doc.xpath("//form")
                    for node in nodes_tree:
                        node.set('delete', '0')
                elif view_type == 'kanban':
                    nodes_tree = doc.xpath("//kanban")
                    for node in nodes_tree:
                        node.set('delete', '0')
                res['arch'] = etree.tostring(doc)
        else:
            if view_type in ['tree']:
                if view_type == 'tree':
                    nodes_tree = doc.xpath("//tree")
                    for node in nodes_tree:
                            node.set('multi_edit', '1')
                res['arch'] = etree.tostring(doc)
        if sm:
            sale_team = self.env['crm.team'].sudo().search([('sale_manager_ids', 'in', self.env.user.id)])

            if view_type in ['form', 'tree']:
                # nodes = doc.xpath("//field[@name='source_id']")
                # for node in nodes:
                #     options = safe_eval(node.get('options', '{}'))
                #     options['no_open'] = 1
                #     node.set('options', repr(options))

                nodes = doc.xpath("//field[@name='user_id']")
                for node in nodes:
                    domain = safe_eval(node.get('domain', '[]'))
                    domain.append(('id', '=', sale_team.mapped('member_ids').ids + sale_team.mapped('user_id').ids))
                    node.set('domain', repr(domain))
                nodes = doc.xpath("//field[@name='team_id']")
                for node in nodes:
                    domain = [('company_id','=',self.env.company.id)]
                    domain.append(('id', '=', sale_team.ids))
                    node.set('domain', repr(domain))
                res['arch'] = etree.tostring(doc)
        if not cm:
            if view_type in ['form', 'tree']:
                for node in doc.xpath("//field"):
                    if node.attrib.get('name') in ['referred', 'source_id','medium_id', 'campaign_id']:
                        modifiers = json.loads(node.get("modifiers"))
                        # modifiers['readonly'] = True
                        modifiers['mo'] = True
                        modifiers['force_save'] = True
                        node.set("modifiers", json.dumps(modifiers))
                        options = safe_eval(node.get('options', '{}'))
                        options['no_open'] = 1
                        node.set('options', repr(options))
                    if node.attrib.get('name') in ['project_id']:
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['force_save'] = True
                        node.set("modifiers", json.dumps(modifiers))
                        options = safe_eval(node.get('options', '{}'))
                        options['no_open'] = 1
                        node.set('options', repr(options))

                res['arch'] = etree.tostring(doc)
            if not cm:
                if view_type in ['form', 'tree']:
                    for node in doc.xpath("//field"):
                        if node.attrib.get('name') in ['referred', 'source_id', 'medium_id', 'campaign_id']:
                            modifiers = json.loads(node.get("modifiers"))
                            # modifiers['readonly'] = True
                            modifiers['mo'] = True
                            modifiers['force_save'] = True
                            node.set("modifiers", json.dumps(modifiers))
                            options = safe_eval(node.get('options', '{}'))
                            options['no_open'] = 1
                            node.set('options', repr(options))
                        if node.attrib.get('name') in ['project_id']:
                            modifiers = json.loads(node.get("modifiers"))
                            modifiers['force_save'] = True
                            node.set("modifiers", json.dumps(modifiers))
                            options = safe_eval(node.get('options', '{}'))
                            options['no_open'] = 1
                            node.set('options', repr(options))

                    res['arch'] = etree.tostring(doc)

        return res