# -*- coding: utf-8 -*-
from odoo import api, fields, models
import time
from datetime import datetime, timedelta
from dateutil import relativedelta




class construction_project(models.Model):
    _inherit = 'construction.project'

    date_from = fields.Date(string='من تاريخ', required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='إلى تاريخ', required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

    total_receive_order = fields.Float(string='إجمالي أوامر الاستلام', readonly=True, compute='_amount_all', tracking=True)
    total_labor = fields.Float(string='إجمالي العمالة', readonly=True, compute='_amount_all', tracking=True)
    total_machine = fields.Float(string='إجمالي المعدات', readonly=True, compute='_amount_all', tracking=True)
    total_tool = fields.Float(string='إجمالي الأدوات', readonly=True, compute='_amount_all', tracking=True)
    total_component = fields.Float(string='إجمالي المكونات', readonly=True, compute='_amount_all', tracking=True)
    total_detialed_cost = fields.Float(string='إجمالي التكلفة التفصيلية', readonly=True, compute='_amount_all', tracking=True)



    @api.depends('project_description','receive_order_ids.total_amount','labor_ids.total_cost','machine_ids.total_cost','tool_ids.total_cost','project_component_ids.component_cost')
    def _amount_all(self):
        for recorde in self:
            total_receive_order = total_labor = total_machine = total_tool = total_component = 0.0
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

            recorde.total_component = total_component
            recorde.total_receive_order = total_receive_order
            recorde.total_labor = total_labor
            recorde.total_machine = total_machine
            recorde.total_tool = total_tool
            recorde.total_detialed_cost = total_receive_order + total_labor + total_machine + total_tool + total_component

