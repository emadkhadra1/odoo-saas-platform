# -*- coding: utf-8 -*-

# from openerp.osv.orm import setup_modifiers
from odoo.tools.translate import _
from odoo import models, fields, api
# from openerp.exceptions import Warning
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning

from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError

class construction_service(models.Model):
    _name = 'construction.service'
    _rec_name = 'name'
    _description = 'construction_service'

    
    def unlink(self):
        if self.state == 'done':
            raise UserError(_('You cannot delete .'))
        return super(construction_service, self).unlink()
    def _get_date_now(self):
        res = datetime.now()
        return res
    
    def confirm(self):

        self.state='done'
        return True
    
    @api.depends('service_machine_ids', 'service_machine_ids.cost',
                 'service_labor_ids', 'service_labor_ids.cost')
    def _compute_total(self):

        total_cost = 0

        if self.service_machine_ids:
            for line in self.service_machine_ids:
                total_cost += line.cost
        if self.service_labor_ids:
            for line in self.service_labor_ids:
                total_cost += line.cost

        self.total_cost = total_cost
        return True

    total_amount = fields.Float(string="Total Amount", compute="_compute_total", store=True, required=False, )
    total_cost = fields.Float(string="Total Cost", compute="_compute_total", store=True, required=False, )
    name = fields.Char(string="Serial", required=False, )
    project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=True, )
    date = fields.Date(string="Date", default=_get_date_now, required=False, )
    state = fields.Selection(string="State", default='new', selection=[('new', 'New'), ('done', 'Done'), ],
                             required=False, )
    service_labor_ids = fields.One2many(comodel_name="construction.service.labor.line", inverse_name="service_id",
                                       string="Service Labor Lines", required=False, )

    service_machine_ids = fields.One2many(comodel_name="construction.service.machine.line", inverse_name="service_id",
                                       string="Service Machine Lines", required=False, )

    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('construction.service.madina')) or 'New'
        res = super(construction_service, self).create(vals)
        # res.update_message_follower()
        return res


class construction_service_machine_line(models.Model):
    _name = 'construction.service.machine.line'

    _description = 'construction_service_machine_line'

    
    @api.depends('unit_cost', 'qty')
    def _compute_cost(self):
        cost = 0
        if self.unit_cost and self.qty:
            cost = self.qty * self.unit_cost
        self.cost = cost
        return True



    @api.onchange('machine_id')
    def onchange_machine_id(self):

        if self.machine_id:
            self.name=self.machine_id.name
            self.unit_cost=self.machine_id.unit_cost




    machine_id = fields.Many2one(comodel_name="construction.machine", string="Machine", required=True, )
    name = fields.Char(string="Titel", required=True, )
    service_id = fields.Many2one(comodel_name="construction.service", string="Service", required=False, )
    unit_cost = fields.Float(string="Uint Cost", required=True, )
    qty = fields.Float(string="Qty",default=1, required=True, )
    cost = fields.Float(string="Cost", compute="_compute_cost", store=True, required=False, )




class construction_machine(models.Model):
    _name = 'construction.machine'

    name = fields.Char(string="Name", required=True, )
    unit_cost = fields.Float(string="Cost",  required=False, )
    unit_price = fields.Float(string="Price",  required=False, )
    note = fields.Text(string="Note", required=False, )

    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('construction.machine.madina')) or 'New'
        res = super(construction_machine, self).create(vals)
        # res.update_message_follower()
        return res


class construction_service_labor_line(models.Model):
    _name = 'construction.service.labor.line'

    _description = 'construction_service_labor_line'

    
    @api.depends('unit_cost', 'qty')
    def _compute_cost(self):
        cost = 0
        if self.unit_cost and self.qty:
            cost = self.qty * self.unit_cost
        self.cost = cost
        return True


    @api.onchange('labor_id')
    def onchange_labor_id(self):

        if self.labor_id:
            self.name = self.labor_id.name
            self.unit_cost = self.labor_id.unit_cost

    labor_id = fields.Many2one(comodel_name="construction.labor", string="Labor", required=True, )
    product_uom_id = fields.Many2one( 'uom.uom', string='Unit of Measure', related='labor_id.product_uom_id',store=True,readonly=True)

    name = fields.Char(string="Titel", required=False, )
    service_id = fields.Many2one(comodel_name="construction.service", string="Service", required=False, )
    unit_cost = fields.Float(string="Uint Cost", required=True, )
    qty = fields.Float(string="Qty", default=1, required=True, )
    cost = fields.Float(string="Cost", compute="_compute_cost", store=True, required=False, )


class construction_labor(models.Model):
    _name = 'construction.labor'

    name = fields.Char(string="Name", required=True)
    product_uom_id = fields.Many2one( 'uom.uom', string='Unit of Measure',  )

    unit_cost = fields.Float(string="Cost",  required=False, )
    unit_price = fields.Float(string="Price",  required=False, )
    note = fields.Text(string="Note", required=False, )

    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('construction.labor.madina')) or 'New'
        res = super(construction_labor, self).create(vals)
        # res.update_message_follower()
        return res
