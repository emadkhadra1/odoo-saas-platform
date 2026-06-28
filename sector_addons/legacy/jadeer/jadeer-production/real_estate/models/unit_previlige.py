# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError
import datetime


class UnitPrivilege(models.Model):
    _name = 'unit.privilege'
    _description = 'Unit Privilege'
    _rec_name = 'privilege_id'


    privilege_id = fields.Many2one(comodel_name="privilege.privilege", string="Privilege",
                                   required=True)
    percent = fields.Float(string="Percent", required=True, )
    description = fields.Char(string="Description", required=False, )
    product_id = fields.Many2one(comodel_name="product.template", string="", required=False, )

    @api.onchange('privilege_id')
    def onchange_privilege_id(self):
        if self.privilege_id:
            pro_pri = self.env['project.privilege'].search([('privilege_id','=',self.privilege_id.id)],limit=1)
            self.percent = pro_pri.percent
