# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccessibleEmployeeInfo(models.Model):
    _name = 'accessible.emp.info'
    _rec_name = 'tab_name'
    _description = 'Assign access to Emp. Info in Portal'

    tab_name = fields.Selection(string="Tab Name", selection=[('work_info', 'Work Information'),
                                                              ('private_info', 'Private Information'),
                                                              # ('medical_insurance', 'Medical Insurance'),
                                                              # ('family_info', 'Family'),
                                                              ], required=False, )
    # name = fields.Many2one(comodel_name="accessible.tabs.info",   required=True )
    tab_field_ids = fields.Many2many(comodel_name="ir.model.fields", string="Fields")
    available_for = fields.Selection(selection=[('all_employees', 'All Employees'),
                                                ('specific_employees', 'Specific Employees'), ],
                                     default="all_employees", required=False, )
    employees_ids = fields.Many2many(comodel_name="hr.employee")

    # @api.onchange('name')
    # def _onchange_name(self):
    #     if self.name:
    #         return {'domain': {'tab_field_ids': [('id', 'in', self.name.tab_field_ids.ids)]}}


class AccessibleTabsInfo(models.Model):
    _name = 'accessible.tabs.info'
    _description = 'Assign access to Tabs. Info in Portal'

    name = fields.Char(string="Tab Name", required=True)
    tab_field_ids = fields.Many2many(comodel_name="ir.model.fields", string="Fields", domain="[('model','=','hr.employee')]")
