# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ProductTemplateInherited(models.Model):
    _inherit = 'product.template'

    manual_creation_name = fields.Boolean(string="Name Manual Creation", )

    @api.onchange('is_composite')
    def onchange_is_composite(self):
        for record in self:
            if record.is_composite:
                record.manual_creation_name = True
                record.is_residential = True
    # @api.onchange('is_residential', 'product_areas', 'building_code', 'product_project', 'unit_code')
    # def calculate_coding(self):
    #     for record in self:
    #         record.num_temp = ''
    #         if record.is_residential:
    #             if record.product_areas:
    #                 area = str(record.product_areas.code)
    #             else:
    #                 area = ''
    #             if record.product_project:
    #                 project = record.product_project.code
    #             else:
    #                 project = ''
    #             if record.building_code:
    #                 building = record.building_code
    #             else:
    #                 building = ''
    #             if record.unit_code:
    #                 code = record.unit_code
    #             else:
    #                 code = ''
    #             record.name = str(area) + str(project) + str(building) + str(code)

    @api.model
    def create(self, vals):
        if vals.get('is_residential') and not vals.get('manual_creation_name'):
            product_project_id = vals['project_id']
            product_project = self.env['real.estate.project'].browse(product_project_id)
            building_code = vals['building_code']
            if building_code:
                building_code = self.env['project.building'].browse(vals['building_code'])
                building_code = building_code.code
            else:
                building_code = False
            floor = vals['floor']
            if floor:
                floor = self.env['building.floor'].browse(vals['floor'])
                floor = floor.code or floor.name
            else:
                floor = False
            unit_code = vals['unit_code']
            name = '{}-{}-{}-{}'.format(
                product_project.code,
                building_code,
                floor,
                unit_code, )
            products = self.search([('name', '=', name)])
            if products:
                raise ValidationError("You can't duplicate because product name is unique")
            else:
                vals['name'] = name
        return super(ProductTemplateInherited, self).create(vals)

    @api.constrains('is_residential', 'floor', 'building_code', 'project_id', 'unit_code')
    def calculate_coding(self):
        for record in self:
            if record.is_residential and not record.is_composite and not record.manual_creation_name:
                name = '{}-{}-{}-{}'.format(
                    record.project_id.code,
                    record.building_code.code,
                    record.floor.code or record.floor.name,
                    record.unit_code, )
                products = self.search([('name', '=', record.name)])
                if len(products) > 1:
                    raise ValidationError("There's another unit with the same name")
                else:
                    record.name = name


class ProductArea(models.Model):
    _name = 'product.area'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('code', required=True, translate=True)
    product_id = fields.Many2one('product.template')


class ProductBuilding(models.Model):
    _name = 'product.building'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('code', required=True, translate=True)
    product_id = fields.Many2one('product.template')
