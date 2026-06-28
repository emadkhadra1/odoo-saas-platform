# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class custody(models.Model):
    _name = 'custody.custody'
    _rec_name = 'employee'
    _order = 'date desc'
    _inherit = ['mail.thread']

    employee = fields.Many2one('hr.employee', 'Employee', tracking=True, required='1')
    equipment_id = fields.Many2one('custody.equipment', 'Equipment', tracking=True, required='1', )
    department = fields.Many2one('hr.department', 'Department')
    date = fields.Datetime('Request Date', default=datetime.now(), tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner', tracking=True)
    deliv_date = fields.Datetime('Delivery Date',
                                 states={'delivery': [('readonly', '1')]}, tracking=True)
    state = fields.Selection(selection=[
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('delivery', 'Deliverd'),
        ('cancel', 'Canceled'),
        ('close', 'Closed')
    ], tracking=True,
        default='new')

    @api.onchange("employee")
    def onchange_employee(self):
        if self.employee:
            self.department = self.employee.id

    def action_new(self):
        self.state = 'new'

    def action_progress(self):
        self.state = 'progress'

    def action_delivery(self):
        self.deliv_date = datetime.now()
        self.state = 'delivery'

    def action_cancel(self):
        self.equipment_id.is_open = False
        self.state = 'cancel'

    def action_close(self):
        self.equipment_id.is_open = False
        self.state = 'close'

    @api.model
    def create(self, vals):
        newrecord = super(custody, self).create(vals)
        newrecord.equipment_id.is_open = True
        return newrecord
