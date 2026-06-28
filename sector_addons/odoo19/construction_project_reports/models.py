# -*- coding: utf-8 -*-
from odoo import api, fields, models
import time
from datetime import datetime, timedelta
from dateutil import relativedelta




class construction_project(models.Model):
    _inherit = 'construction.project'

    date_from = fields.Date(string='Date From', required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Date To', required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

    total_receive_order = fields.Float(string='Total Receive Order', readonly=True, compute='_amount_all', tracking=True)
    total_labor = fields.Float(string='Total Labor', readonly=True, compute='_amount_all', tracking=True)
    total_machine = fields.Float(string='Total Machine', readonly=True, compute='_amount_all', tracking=True)
    total_tool = fields.Float(string='Total Tool', readonly=True, compute='_amount_all', tracking=True)
    total_component = fields.Float(string='Total Component', readonly=True, compute='_amount_all', tracking=True)
    total_detialed_cost = fields.Float(string='Total Detialed Cost', readonly=True, compute='_amount_all', tracking=True)



    @api.depends('project_description','receive_order_ids.total_amount','labor_ids.total_cost','machine_ids.total_cost','tool_ids.total_cost','project_component_ids.component_cost')
    def _amount_all(self):
        total_receive_order= total_labor = total_machine=total_tool = total_component = 0.0
        for recorde in self:
            for component_line in recorde.project_component_ids:
                total_component += component_line.component_cost

            for receive_order_line in recorde.receive_order_ids:
                if receive_order_line.state == 'done' or receive_order_line.state == 'delivered':
                    total_receive_order += receive_order_line.total_cost

            for labor_line in recorde.labor_ids:
                if labor_line.state == 'done':
                    total_labor += labor_line.total_cost

            for machine_line in recorde.machine_ids:
                if machine_line.state == 'done':
                    total_machine += machine_line.total_cost

            for tool_line in recorde.tool_ids:
                if tool_line.state == 'done':
                    total_tool += tool_line.total_cost



            self.total_component=total_component
            self.total_receive_order=total_receive_order
            self.total_labor=total_labor
            self.total_machine=total_machine
            self.total_tool=total_tool
            self.total_detialed_cost=total_receive_order+total_labor+total_machine+total_tool+total_component


