# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class CustodyEquipment(models.Model):
    _name = 'custody.equipment'
    _rec_name = 'equipment'
    _inherit = ['mail.thread']
    equipment = fields.Char('Name', required='1')
    code = fields.Char('Code', required='1')
    serial = fields.Char('Serial Num', tracking=True)
    bio = fields.Text('Bio', tracking=True)
    category_id = fields.Many2one('equipment.category', 'Category', tracking=True)
    item_id = fields.Many2many('equipment.item', string='Item')
    item_ids = fields.One2many(comodel_name="equipment.item.line", inverse_name="equip", required=False, string='Item')
    value = fields.Text('Value')
    is_open = fields.Boolean('Open?')


class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _rec_name = 'item'
    _inherit = ['mail.thread']
    item = fields.Char('Name', required='1', tracking=True, )
    code = fields.Char('ID', required='1', tracking=True)
    value = fields.Char('Value')


class EquipmentItemLINE(models.Model):
    _name = 'equipment.item.line'
    _rec_name = 'items'

    items = fields.Many2one(comodel_name="equipment.item", string='Item')
    code_id = fields.Char(string="ID", related="items.code")
    value_id = fields.Char(string="Value")
    equip = fields.Many2one(comodel_name="custody.equipment", string="Equipment", required=False, )
