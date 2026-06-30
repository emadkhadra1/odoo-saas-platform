# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class AnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'

    is_unit_property = fields.Boolean()
    # is_delivered = fields.Boolean('Delivered')
    # total_meter = fields.Float('Total Area(m)', compute='calc_project_units_area')
    # unit_type_ids = fields.Many2many(comodel_name="unit.type")
    # filter_attached_areas_ids = fields.Many2many(comodel_name="attached.area",compute="get_filter_attached_areas")
    # attached_areas_ids = fields.Many2many(comodel_name="attached.area")
    # product_areas = fields.Many2one('product.area', track_visibility='onchange', )
    # singularity_ids = fields.Many2many(comodel_name="privilege.privilege", string="Singularities", )

    # @api.depends('unit_type_ids')
    # def get_filter_attached_areas(self):
    #     for rec in self:
    #         if rec.unit_type_ids:
    #             rec.filter_attached_areas_ids = self.env['attached.area'].search([('unit_type_id','in',rec.unit_type_ids.ids)]).ids
    #         else:
    #             rec.filter_attached_areas_ids = False
    #
    #
    # def calc_project_units_area(self):
    #     for rec in self:
    #         units = self.env['product.template'].search([('product_project', '=', rec.id)])
    #         total_area = sum(units.mapped('total_Area'))
    #         total_area += sum(units.mapped('land_area'))
    #         total_area += sum(units.mapped('extra_land'))
    #         rec.total_meter = total_area
    #
    # def button_delivery(self):
    #     self.is_delivered = True
    #
    # def button_accounting_entry(self):
    #     ctx = self.env.context.copy()
    #     ctx.update({'from_project': True, 'create': False, 'edit': False})
    #     return {
    #         'name': _('Delivered Units'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'list',
    #         'res_model': 'product.template',
    #         # 'view_id': compose_form.id,
    #         'target': 'current',
    #         'domain': [
    #             ('state', '=', 'sold'),
    #             ('unit_deleivery', '=', False),
    #             ('product_project', '=', self.id)
    #         ],
    #         'context': {'from_project': True, 'create': False, 'edit': False},
    #     }
    #
    # def action_open_costing_entry(self):
    #     ctx = self.env.context.copy()
    #     ctx.update({'from_project': True, 'create': False, 'edit': False})
    #     moves = self.env['product.template'].search([('product_project', '=', self.id)]).mapped('move_ids')
    #     return {
    #         'name': _('Costing Entries'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'list,form',
    #         'res_model': 'account.move',
    #         'target': 'current',
    #         'domain': [('id', 'in', moves.ids)],
    #         'context': {'create': False, 'edit': False},
    #     }
