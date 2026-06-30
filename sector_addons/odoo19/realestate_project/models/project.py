# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from datetime import timedelta

class RealEstateProject(models.Model):
    _name = "real.estate.project"
    name = fields.Char()
    code = fields.Char()
    penalty_percentage = fields.Float(string='Penalty Percentage')
    property_account_receivable_id = fields.Many2one('account.account', string='Receivable Account',store=True,readonly=False,related='analytic_account_id.property_account_receivable_id', domain=lambda x: [
        ('user_type_id', '=', x.env.ref('account.data_account_type_receivable').id)], company_dependent=True)
    credit_account_id = fields.Many2one('account.account', 'Credit Account', company_dependent=True)
    journal_id = fields.Many2one('account.journal', 'Journal', company_dependent=True)
    cost_credit_account_id = fields.Many2one('account.account', 'Costing Account', company_dependent=True)
    cost_debit_account_id = fields.Many2one('account.account', 'Project Under Construction', company_dependent=True)
    cost_journal_id = fields.Many2one('account.journal', 'Journal', company_dependent=True)
    property_stock_valuation_account_id = fields.Many2one('account.account', 'Valuation Account', company_dependent=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', company_dependent=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    image_128 = fields.Image('Image', readonly=False)
    image_ids = fields.One2many('project.image', 'project_id', string='Project Images')
    docs_ids = fields.Many2many('ir.attachment', 'project_attach_rel','project_id','attach_id', string='Other Materials')
    # docs_ids = fields.one2many('project.other.attachment', 'project_id', string='Other Attachments')
    map_url = fields.Char('Map URL')
    @api.model
    def create(self,vals):
        res = super(RealEstateProject, self).create(vals)
        analytic_account = self.env['account.analytic.account'].create({
            'name': res.name,
            'code':res.code ,
            'company_id': res.company_id.id,
            'property_account_receivable_id': res.property_account_receivable_id.id,
        })
        res.analytic_account_id = analytic_account.id
        return res
    def action_image_preview(self):
        images_ids = self.env['project.image'].search([('project_id', '=', self.id)])
        compose_form = self.env.ref('realestate_project.real_image_preview_form')
        if not images_ids:
            raise ValidationError("There Is No Images To View")
        else:
            return {
                'name': 'Image Preview',
                'view_mode': 'form',
                'res_model': 'project.image.preview',
                'type': 'ir.actions.act_window',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': {
                    'default_project_id': self.id,
                    'default_image_id': images_ids[0].id,
                    'default_image_ids': [(6, 0, self.image_ids.ids)],
                    'default_image_preview': images_ids[0].image,
                },
                'target': 'current',
            }

    def open_project_units(self):
        views = [
            (self.env.ref('product.product_template_kanban_view').id, 'kanban'),
            (self.env.ref('real_estate.product_template_tree_view_inherit').id, 'tree'),
            (self.env.ref('product.product_template_only_form_view').id, 'form'),
        ]
        return {
            'name': 'Units',
            'view_mode': 'kanban,list,form',
            'res_model': 'product.template',
            'views': views,
            'type': 'ir.actions.act_window',
            'context': {
                'default_project_id': self.id,
            },
            'domain':[('project_id','=',self.id)],
            'target': 'current',
        }