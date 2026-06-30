# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class Project(models.Model):
    _inherit = 'real.estate.project'

    # is_unit_property = fields.Boolean()
    is_delivered = fields.Boolean('Delivered')
    total_meter = fields.Float('Total Area(sm)', compute='calc_project_units_area')
    unit_type_ids = fields.Many2many(comodel_name="unit.type")
    filter_attached_areas_ids = fields.Many2many(comodel_name="attached.area",compute="get_filter_attached_areas")
    attached_areas_ids = fields.Many2many(comodel_name="attached.area")
    product_areas = fields.Many2one('product.area', track_visibility='onchange',string="Location" )
    # singularity_ids = fields.Many2many(comodel_name="privilege.privilege", string="Singularities", )

    project_singularity_ids = fields.One2many(comodel_name="project.privilege", inverse_name="project_id", string="Project Privileges",
                                      required=False, )
    project_utility_ids = fields.One2many(comodel_name="project.utility", inverse_name="project_id", string="Utilities",
                                      required=False, )
    car_spot = fields.Boolean(string="", )
    car_spot_price = fields.Float()
    parking_code = fields.Char('Parking Code')
    payment_plan_ids = fields.Many2many('payment.plan',string="Payment Plans",ondelete='cascade'  )
    reserve_days_no = fields.Integer(string="No. of Reservation Days ",)


    @api.constrains('project_singularity_ids','project_utility_ids')
    def check_Repetition(self):
        for rec in self:
            priv_list = [x.privilege_id.prev_id.name for x in rec.project_singularity_ids]
            priv_list = list(set(priv_list))
            if len(rec.project_singularity_ids) > len(priv_list):
                raise exceptions.ValidationError("Singularities can't be repeated")
            util_list = [x.utility_id.name for x in rec.project_utility_ids]
            util_list = list(set(util_list))
            if len(rec.project_utility_ids) > len(util_list):
                raise exceptions.ValidationError("Utilities can't be repeated")
    @api.depends('unit_type_ids')
    def get_filter_attached_areas(self):
        for rec in self:
            if rec.unit_type_ids:
                rec.filter_attached_areas_ids = self.env['attached.area'].search([('unit_type_id','in',rec.unit_type_ids.ids)]).ids
            else:
                rec.filter_attached_areas_ids = False


    def calc_project_units_area(self):
        for rec in self:
            units = self.env['product.template'].search([('project_id', '=', rec.id),('active', '=', True),('is_composite','=',False)])
            total_area = sum(units.mapped('total_Area'))
            total_area += sum(units.mapped('land_area'))
            total_area += sum(units.mapped('extra_land'))
            rec.total_meter = total_area

    def button_delivery(self):
        self.is_delivered = True

    def button_accounting_entry(self):

        ctx = self.env.context.copy()
        ctx.update({'from_project': True, 'create': False, 'edit': False})
        return {
            'name': _('Delivered Units'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'product.template',
            # 'view_id': compose_form.id,
            'target': 'current',
            'domain': [
                ('state', '=', 'sold'),
                ('unit_deleivery', '=', False),
                ('project_id', '=', self.id)
            ],
            'context': {'from_project': True, 'create': False, 'edit': False},
        }

    def action_open_costing_entry(self):
        ctx = self.env.context.copy()
        ctx.update({'from_project': True, 'create': False, 'edit': False})
        moves = self.env['product.template'].search([('project_id', '=', self.id)]).mapped('move_ids')
        return {
            'name': _('Costing Entries'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('id', 'in', moves.ids)],
            'context': {'create': False, 'edit': False},
        }

class ProjectPrivilege(models.Model):
    _name = 'project.privilege'
    _description = 'Project Privilege'
    _rec_name = 'privilege_id'
    privilege_id = fields.Many2one(comodel_name="privilege.privilege", string="Privilege",
                                   required=True,ondelete='cascade')
    percent = fields.Float(string="Percent", required=True, )
    project_id = fields.Many2one(comodel_name="real.estate.project", string="", required=False, )
    @api.constrains('percent')
    def _check_percent(self):
        for rec in self:
            if rec.percent <= 0.0:
                raise exceptions.ValidationError('Singularity Percent Must Be > 0')



class ProjectUtility(models.Model):
    _name = 'project.utility'

    utility_id = fields.Many2one('utility.utility',string='Utility', )
    type = fields.Selection(string="Type", selection=[('percent', 'Percent'), ('amount', 'Amount'), ], required=True, )
    percent = fields.Float('Value')
    project_id = fields.Many2one('real.estate.project')
    @api.constrains('percent','type')
    def _check_percent(self):
        for rec in self:
            if rec.type == 'percent':
                if rec.percent <= 0.0:
                    raise exceptions.ValidationError('Utility Percent Must Be > 0')
            elif rec.type == 'amount':
                if rec.percent <= 0.0:
                    raise exceptions.ValidationError('Utility Amount Must Be > 0')

