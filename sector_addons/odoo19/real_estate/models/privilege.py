# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime


class Privileges(models.Model):
    _name = 'privilege.privilege'
    _rec_name = 'prev_id'

    prev_id = fields.Many2one(comodel_name="privilege.name", string="Privilege", required=False, )
    description = fields.Char(string="Description", required=False, )
    percent = fields.Float('Percent(%)')

    # @api.constrains('percent')
    # def _check_percent(self):
    #     for rec in self:
    #         if rec.percent < 0.0:
    #             raise exceptions.ValidationError('Percent Must Be >= 0')
    #         elif rec.percent >= 100:
    #             raise exceptions.ValidationError('Percent Must Be < 100')


class Privilegename(models.Model):
    _name = 'privilege.name'

    name = fields.Char(string="Name", required=False, )
