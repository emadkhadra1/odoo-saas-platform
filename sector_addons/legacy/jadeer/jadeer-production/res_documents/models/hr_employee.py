# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        rec = super(Employee, self).create(vals)
        if vals.get('country_id'):
            country_id = self.env['res.country'].browse(vals.get('country_id'))
            rec.create_employee_required_document(country_id)
        return rec

    def write(self, vals):
        super(Employee, self).write(vals)
        if vals.get("country_id"):
            for rec in self:
                country_id = self.env['res.country'].browse(vals.get('country_id'))
                rec.create_employee_required_document(country_id)
        return True

    def create_employee_required_document(self, country_id):
        required_types = self.env.user.company_id.egyptian_employee_document_ids
        exist_types = self.document_ids.mapped('type_id')
        todo_types = (required_types - exist_types)
        self.create_document(todo_types)

    def create_document(self, types):
        vals = []
        for typ in types:
            vals.append({
                'employee_id': self.id,
                'type_id': typ.id,
            })
        self.env['res.documents'].create(vals)
