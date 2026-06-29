# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
# from openerp.osv.orm import setup_modifiers
# from openerp.tools.translate import _
# from openerp import models, fields, api
# from openerp.exceptions import Warning
from datetime import date


from datetime import datetime, date

# from reportlab.graphics.widgetbase import Face
from odoo.exceptions import UserError, ValidationError


class ProjectBOQS(models.Model):
    _name = 'project.boq'

    boq_name = fields.Char(string="BOQ Name", required=False, )
    boq_type = fields.Char(string="BOQ Type", required=False, )
    boq_date = fields.Date(string="BOQ Date", required=False, )
    boq_total_cost = fields.Float(string="BOQ Total Cost", required=False, )
    boq_total_sell = fields.Float(string="BOQ Total Sell", required=False, )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project id",
                                              required=False, )
    bom_id = fields.Integer(string="ID", required=False, )

    def action_show_bom(self):
        print("lllllllllllll", self.bom_id)
        return {
            'name': _('SHOW'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'b2b.construction.boq',
            'res_id': self.bom_id,
        }


class construction_project(models.Model):
    _name = 'construction.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'construction.project'

    def _get_date_now(self):
        res = datetime.now()
        return res

    def _get_warehouse_id(self):
        res = False
        company_id = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)], )
        res = warehouse_ids[0]
        print('warehouse_id=' + str(res.id))

        return res

    def _get_analytic_plan_id(self):
        plan = self.env['account.analytic.plan'].search([('name', '=', 'Project')], limit=1)
        if not plan:
            plan = self.env['account.analytic.plan'].search([], limit=1)
        if not plan:
            plan = self.env['account.analytic.plan'].create({
                'name': 'Project',
                'default_applicability': 'optional',
            })
        return plan.id

    @api.model_create_multi
    def create(self, vals_list):
        projects = self.browse()
        for vals in vals_list:
            stock_location = False
            project_name = vals.get('name')
            partner_id = vals.get('partner_id')

            if partner_id and project_name:
                stock_location_vals = {
                    'name': project_name,
                    'usage': 'internal',
                }
                parent_location_id = vals.get('location_id')
                if not parent_location_id:
                    warehouse = self.env['stock.warehouse'].browse(vals.get('warehouse_id')) if vals.get('warehouse_id') else self._get_warehouse_id()
                    parent_location_id = warehouse.lot_stock_id.id or warehouse.view_location_id.id
                if parent_location_id:
                    stock_location_vals['location_id'] = parent_location_id

                stock_location = self.env['stock.location'].create(stock_location_vals)
                vals.update({
                    'location_dest_id': stock_location.id,
                    'location_create': True,
                })

                if not vals.get('analytic_account_id'):
                    analytic_account = self.env['account.analytic.account'].create({
                        'name': project_name,
                        'partner_id': partner_id,
                        'plan_id': self._get_analytic_plan_id(),
                    })
                    vals['analytic_account_id'] = analytic_account.id

            project = super(construction_project, self).create([vals])
            if stock_location and not project.location_dest_id:
                project.location_dest_id = stock_location.id
            projects |= project
        return projects

    def write(self, vals):
        if self.partner_id and self.name and self.location_dest_id and False:
            self.location_dest_id.write({'name': self.name, 'partner_id': self.partner_id.id})

        project = super(construction_project, self).write(vals)

        return project

    # 
    # @api.depends('partner_id','name','location_create' )
    # def _compute_dest_id(self):
    #     if self.partner_id and self.name:
    #         if self.location_dest_id:
    #             self.location_dest_id.write({'name':self.name,'partner_id':self.partner_id.id})
    #             action=False
    #         else:
    #             if not self.location_create and  not self.location_dest_id:
    #
    #             # self.write({'location_dest_id':stock_location.id,'location_create':True})
    #
    #     return True

    @api.depends('warehouse_id')
    def _compute_location_id(self):

        if self.warehouse_id and self.warehouse_id.out_type_id:
            self.picking_type_id = self.warehouse_id.out_type_id.id
            if self.warehouse_id.out_type_id.default_location_src_id:
                self.location_id = self.warehouse_id.out_type_id.default_location_src_id.id
                # self.location_dest_id = self.warehouse_id.out_type_id.default_location_dest_id.id
        return True

        # return True

    picking_type_id = fields.Many2one('stock.picking.type', compute="_compute_location_id", store=True,
                                      string='Picking Type')

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", default=_get_warehouse_id,
                                   string="Warehouse", required=True, )
    location_id = fields.Many2one('stock.location', 'Source Location', compute="_compute_location_id", store=True,
                                  required=False)
    primary_insurance = fields.Char(string="Primary Insurance", required=False, )

    location_dest_id = fields.Many2one('stock.location', 'Destination Location R',
                                       store=True, required=False, readonly=False)
    location_create = fields.Boolean(string="location_create", )

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    name = fields.Char("Project Name", required=True, )

    partner_id = fields.Many2one(comodel_name="res.partner", string="partner", required=True,
                                 domain=[('customer_rank', '=', 1)])

    project_description = fields.Text(string="Project Description", required=False, )

    project_unit_ids = fields.One2many(comodel_name="project.unit", inverse_name="project_id",
                                       string="Project Unit Lines", required=False, )

    project_item_ids = fields.One2many(comodel_name="project.item", inverse_name="project_id",
                                       string="Project Item Lines", required=False, )

    project_component_ids = fields.One2many(comodel_name="project.component", inverse_name="project_id",
                                            string="Project Component Lines", required=False, )

    labor_ids = fields.One2many(comodel_name="construction.labor", inverse_name="project_id", string="Labors",
                                required=False, )
    machine_ids = fields.One2many(comodel_name="construction.machine", inverse_name="project_id", string="Machines",
                                  required=False, )
    tool_ids = fields.One2many(comodel_name="construction.tool", inverse_name="project_id", string="ToolS",
                               required=False, )
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    contract_type = fields.Many2one(comodel_name="contract.type", string="Contract Type", required=False, )
    boq_line_ids = fields.One2many(comodel_name="project.boq", inverse_name="construction_project_id",
                                   string="BOQ Lines", required=False, readonly=True)

    @api.depends('project_component_ids.component_cost', 'receive_order_ids',
                 'receive_order_ids.total_cost', 'receive_order_ids.state'
        , 'labor_ids', 'labor_ids.total_cost', 'labor_ids.state'
        , 'machine_ids', 'machine_ids.total_cost', 'machine_ids.state'
        , 'tool_ids', 'tool_ids.total_cost', 'tool_ids.state'

                 )
    def _compute_total_cost(self):
        total_cost = 0
        for one_component in self.project_component_ids:
            total_cost += one_component.component_cost

        for receive_order in self.receive_order_ids:
            if receive_order.state == 'done' or receive_order.state == 'delivered':
                total_cost += receive_order.total_cost

        for one_labor in self.labor_ids:
            if one_labor.state == 'done':
                total_cost += one_labor.total_cost

        for one_machine in self.machine_ids:
            if one_machine.state == 'done':
                total_cost += one_machine.total_cost

        for one_tool in self.tool_ids:
            if one_tool.state == 'done':
                total_cost += one_tool.total_cost

        self.total_cost = total_cost

        return True

    receive_order_ids = fields.One2many(comodel_name="construction.receive.order", inverse_name="project_id",
                                        string="Receive Order", required=False, )

    @api.depends('estimated_costs', 'selling_price')
    def _comp_estimated_net_profit(self):
        estimated_net_profit = 0
        if self.estimated_costs and self.selling_price:
            estimated_net_profit = self.selling_price - self.estimated_costs

        self.estimated_net_profit = estimated_net_profit
        return True

    @api.depends('estimated_costs', 'selling_price')
    def _comp_estimated_profit_margin_ratio(self):
        estimated_profit_margin_ratio = 0
        if self.estimated_costs and self.selling_price and self.estimated_costs > 0:
            estimated_profit_margin_ratio = 100 - ((self.estimated_costs / self.selling_price) * 100)

        self.estimated_profit_margin_ratio = estimated_profit_margin_ratio
        return True

    @api.depends('total_cost', 'selling_price')
    def _comp_net_profit(self):
        net_profit = 0
        if self.total_cost and self.selling_price:
            net_profit = self.selling_price - self.total_cost

        self.net_profit = net_profit
        return True

    @api.depends('total_cost', 'selling_price')
    def _comp_net_profit_ratio(self):
        net_profit_ratio = 0
        if self.total_cost and self.selling_price and self.total_cost > 0:
            net_profit_ratio = (self.selling_price / self.total_cost) * 100

        self.net_profit_ratio = net_profit_ratio
        return True

    total_cost = fields.Float(string="Actual Cost", compute="_compute_total_cost", store=True, required=False, )
    # selling_price = fields.Float(string="Selling Price", required=False, compute='_compute_line_ids_changed')
    selling_price = fields.Float(string="Selling Price", required=False)
    # estimated_costs = fields.Float(string="Estimated Costs", required=False, compute='_compute_line_ids_changed')
    estimated_costs = fields.Float(string="Estimated Costs", required=False)
    estimated_net_profit = fields.Float(string="Estimated Net Profit", compute="_comp_estimated_net_profit", store=True,
                                        required=False, )
    estimated_profit_margin_ratio = fields.Float(string="Estimated Profit Margin Ratio %",
                                                 compute="_comp_estimated_profit_margin_ratio", store=True,
                                                 required=False, )
    net_profit = fields.Float(string="Net Profit", compute="_comp_net_profit", store=True, required=False, )
    net_profit_ratio = fields.Float(string="Net Profit Ratio  %", compute="_comp_net_profit_ratio", store=True,
                                    required=False, )
    purpose_of_the_project = fields.Selection(string="Purpose of the project",
                                              selection=[('ownership', 'Ownership'), ('for_sale', 'For sale'), ],
                                              required=False, )

    # @api.onchange('boq_line_ids')
    # def _compute_line_ids_changed(self):
    #     for rec in self:
    #         estimated_costs = 0
    #         selling_price = 0
    #         for line in rec.boq_line_ids:
    #             selling_price += line.boq_total_sell
    #             estimated_costs += line.boq_total_cost
    #         rec.estimated_costs = estimated_costs
    #         rec.selling_price = selling_price
