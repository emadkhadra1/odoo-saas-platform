# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
# from openerp.osv.orm import setup_modifiers
from odoo.tools.translate import _
# from openerp import models, fields, api
from odoo.exceptions import Warning
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning

from datetime import datetime ,date

# from reportlab.graphics.widgetbase import Face
from odoo.exceptions import UserError, ValidationError


class construction_project(models.Model):
    _name = 'construction.project'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = 'construction.project'

    def _get_date_now(self):
        res = datetime.now()
        return res



    name = fields.Char("Project Name",required=True, )

    partner_id = fields.Many2one(comodel_name="res.partner",    string="partner" , required=True, )

    project_description = fields.Text(string="Project Description", required=False, )

    project_unit_ids = fields.One2many(comodel_name="project.unit", inverse_name="project_id", string="Project Unit Lines", required=False, )

    project_item_ids = fields.One2many(comodel_name="project.item", inverse_name="project_id",
                                       string="Project Item Lines", required=False, )

    project_component_ids = fields.One2many(comodel_name="project.component",   inverse_name="project_id",
                                           string="Project Component Lines", required=False, )


    
    @api.depends( 'project_component_ids.component_cost')
    def _compute_total_cost(self):
        total_cost = 0
        for one_component in self.project_component_ids:
            total_cost += one_component.component_cost

        self.total_cost = total_cost

        return True
    

    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True,
                                        required=False, )





class project_unit(models.Model):
    _name = 'project.unit'
    _rec_name = 'name'
    _description = 'project.unit'


    def _default_project_id(self):
        res=False
        if self._context.get('active_model') == 'construction.project' and self._context.get('active_ids'):

            project = self.env['construction.project'].browse(self._context.get('active_ids'))
            res=project[0]
        return res

    
    @api.depends('project_item_ids', 'project_item_ids.project_component_ids', 'project_item_ids.project_component_ids.component_cost')
    def _compute_total_unit_cost(self):
        total_unit_cost = 0
        for unit in self.project_item_ids:
            for one_component in unit.project_component_ids:
                total_unit_cost += one_component.component_cost

        self.total_unit_cost = total_unit_cost

        return True

    project_id = fields.Many2one(comodel_name="construction.project",   default=_default_project_id, string="Project",  )
    name = fields.Char("Unit Name", required=True, )


    unit_location = fields.Char(string="Unit Location", required=False, )
    unit_description = fields.Text(string="Unit Description", required=False, )


    project_item_ids = fields.One2many(comodel_name="project.item", inverse_name="unit_id",
                                        string="Project Item Lines", required=False, )

    total_unit_cost = fields.Float(string="Total Unit Cost", compute="_compute_total_unit_cost", store=True, required=False, )

states_item_1 = {   'new': [('readonly', False)],'confirm': [('readonly', True)]    }

class project_item(models.Model):
    _name = 'project.item'
    _rec_name = 'name'
    _description = 'project.item'
    _order = 'state DESC'
    
    def unlink(self):

        if self.state == 'confirm':
            raise UserError(_(
                'The operation cannot be completed:\nYou are trying to delete Item Confirmed.'))
        return super(project_item, self).unlink()
    
    @api.depends('unit_id', 'product_id')
    def _compute_item_name(self):
        name = ''
        if self.unit_id and self.product_id:
            name = self.product_id.name + "/" + self.unit_id.name

        self.name = name

        return True

    
    @api.depends('project_component_ids' ,'project_component_ids.component_cost' )
    def _compute_total_item_cost(self):
        total_item_cost=0
        for one_component in self.project_component_ids :
            total_item_cost += one_component.component_cost

        self.total_item_cost = total_item_cost

        return True

    
    @api.depends('item_qty' ,'total_item_cost' )
    def _compute_item_cost(self):
        item_cost=0
        if self.item_qty and self.total_item_cost:
            item_cost=self.total_item_cost  / self.item_qty

        self.item_cost = item_cost

        return True

    
    def cp_item_confirm(self):
        if self.project_component_ids:
            if self.item_qty >0:
                self.action_stock_move()
                for line in self.project_component_ids:
                    line.cp_component_confirm()
                self.state='confirm'
            else:
                raise UserError(_('Error !Cannot Confirm The Item : Itme QTY Must Be > 0 '))

        else:

            raise UserError(_('Error !Cannot Confirm The Item : Make Sure The Item Have At Least One Component.'))

        return True

    
    def action_stock_move(self):
        picking_id = False
        if self.unit_id and self.unit_id.project_id and self.unit_id.project_id.partner_id:
            partner_id = self.unit_id.project_id.partner_id.id
        else:
            partner_id = False
        if self.warehouse_id:
            warehouse_id = self.warehouse_id
        else:
            company_id = self.env.user.company_id.id
            warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)], )
            warehouse_id = warehouse_ids[0]
        # print "warehouse_id"
        # print warehouse_id
        if self.warehouse_id:
            if self.location_id and self.location_dest_id and self.picking_type_id:

                # print  'ready to picking'


                group_id = self.env['procurement.group'].create({

                                  'name': "CP_Item#"+ str(self.id),
                                  'move_type': 'direct',
                    'partner_id': partner_id,
                              })
                rule_id=False
                self.group_id =group_id.id

                for line in self.project_component_ids:
                    origin = "CPC#" + str(line.id)
                    # procurement_id = self.env['procurement.order'].create({
                    #
                    #     'warehouse_id': warehouse_id.id,
                    #     'origin': origin,
                    #     'partner_id': partner_id,
                    #     'product_uom_qty': line.component_qty,
                    #    'product_uom': line.product_id.uom_id.id,
                    #     'location_id': self.location_id.id,
                    #     'location_dest_id': self.location_dest_id.id,
                    #     'picking_type_id': self.picking_type_id.id,
                    #
                    # })
                    # value={
                    #     'name': self.name,
                    #     'origin': self.order_id.name,
                    #     'date_planned': datetime.strptime(self.order_id.date_order,
                    #                                       DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                    #         days=self.customer_lead),
                    #     'product_id': self.product_id.id,
                    #     'product_qty': self.product_uom_qty,
                    #     'product_uom': self.product_uom.id,
                    #     'company_id': self.order_id.company_id.id,
                    #     'group_id': group_id,
                    #     'sale_line_id': self.id
                    # }

                    procurement_id=self.env['procurement.order'].create(
                                {'product_id': line.product_id.id,
                                              'product_qty': line.component_qty,
                                              'product_uom': line.product_uom.id,
                                              'name': "CPL:" +line.name or "CPL#" + str(line.id),
                                              'origin': origin,
                                             'warehouse_id': warehouse_id.id,
                                              'location_id': self.location_dest_id.id,
                                              'company_id': self.company_id.id,
                                              'group_id': group_id.id,
                                              'rule_id':rule_id,
                                              'partner_dest_id':partner_id,
                                              # 'location_dest_id': self.location_dest_id.id,
                                                  })


                    if procurement_id:

                        picking_data= self.env['stock.picking'].search([('origin','=',origin) ] ,   )
                        if(len(picking_data)>0):

                            picking_id=picking_data[0]
                            picking_id.write({'partner_id': partner_id})
                            picking_id.action_confirm()
                            picking_id.action_assign()
                            picking_id.force_assign()
                            picking_id.do_transfer()
                            inventory_value=0
                            valuations = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', picking_id.move_lines.ids)])
                            for quant in valuations:
                                inventory_value += quant.value

                            line.write({'component_cost':inventory_value})
                            #get cost now


                    line.write({'procurement_id':procurement_id.id,'picking_id':picking_id.id})
                    # print origin
                    # print line
                # picking_id = self.env['stock.picking'].create({
                #
                #     'warehouse_id': warehouse_id.id,
                #     'origin': origin,
                #     'partner_id': partner_id,
                #     'location_id': self.location_id.id,
                #     'location_dest_id': self.location_dest_id.id,
                #     'picking_type_id': self.picking_type_id.id,
                #
                # })
                # print "picking_id" + str(picking_id)
                # for line in self.project_component_ids:
                #     self.env['stock.move'].create({'product_id': line.product_id.id,
                #                                    'product_uom_qty': line.component_qty,
                #                                    'product_uom': line.product_id.uom_id.id,
                #                                    'name': line.name or "CPL:" + str(line.product_id.id),
                #                                    'picking_id': picking_id.id,
                #                                    'location_id': self.location_id.id,
                #                                    'location_dest_id': self.location_dest_id.id,
                #                                    })
                # picking_id.action_confirm()
                # picking_id.action_assign()
                # picking_id.force_assign()
                # picking_id.do_transfer()
                # # picking_id.signal_workflow('action_confirm')
                # # picking_id.signal_workflow('action_assign')
                # # picking_id.signal_workflow('force_assign')
                # self.picking_id = picking_id.id
        else:
            msg = ''
            if not warehouse_id:
                msg += '\n - No warehouse assigned to this user '
            if not self.order_type:
                msg += '\n - No data in order_type '
            if not self.order_line:
                msg += '\n - No data in order_line '
            raise UserError('Some Data Is Missing To Cerate Stock Move' + msg)

        return True

    
    def _get_warehouse_id(self):
        res = False
        company_id = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)], )
        res = warehouse_ids[0]
        print ('warehouse_id=' + str(res.id))

        return res



    
    @api.depends('picking_id', 'picking_id.state')
    def _compute_picking_state(self):
        picking_state = ''
        if self.picking_id:
            picking_state = self.picking_id.state

        self.picking_state = picking_state
        return True





        # self.update(values)

    
    @api.depends('unit_id','warehouse_id')
    def _compute_project_id(self):
        project_id=False
        if self.unit_id and self.unit_id.project_id:
            self.project_id=self.unit_id.project_id.id

        if self.unit_id and self.unit_id.project_id and self.unit_id.project_id.partner_id:
            self.location_dest_id = self.unit_id.project_id.partner_id.property_stock_customer.id


        if self.warehouse_id and self.warehouse_id.out_type_id:
            self.picking_type_id = self.warehouse_id.out_type_id.id
            if self.warehouse_id.out_type_id.default_location_src_id:
                self.location_id=self.warehouse_id.out_type_id.default_location_src_id.id




        return True
    unit_id = fields.Many2one(comodel_name="project.unit",states=states_item_1 ,  string="Unit", required=True, )


    project_id = fields.Many2one(comodel_name="construction.project", compute="_compute_project_id",store=True,  string="Project", required=False, )

    location_id = fields.Many2one('stock.location', 'Source Location',compute="_compute_project_id",store=True,  required=False)
    location_dest_id = fields.Many2one('stock.location', 'Destination Location',compute="_compute_project_id",store=True ,  required=False)
    picking_type_id = fields.Many2one('stock.picking.type',compute="_compute_project_id",store=True,  string='Picking Type')

    name = fields.Char(string="Unit Name",compute="_compute_item_name",store=True, required=False, )
    product_id = fields.Many2one(comodel_name="product.product",states=states_item_1 ,  string="Item Product", required=True, )
    product_uom = fields.Many2one('uom.uom',related="product_id.uom_id",store=True, string='Unit of Measure', required=True)
    item_description = fields.Text(string="Item Description",states=states_item_1 ,  required=False, )
    item_qty = fields.Float(string="Item QTY",default=1,  required=True,states=states_item_1 ,  )


    project_component_ids = fields.One2many(comodel_name="project.component", states=states_item_1 , inverse_name="item_id",
                                       string="Project Component Lines", required=False, )
    state = fields.Selection(string="State", default='new' , selection=[('new', 'Draft'), ('confirm', 'Confirm'), ], required=False, )



    total_item_cost = fields.Float(string="Total Item Cost",compute="_compute_total_item_cost",store=True,  required=False, )
    item_cost = fields.Float(string="Item Cost",compute="_compute_item_cost",store=True,  required=False, )

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse",states=states_item_1 ,    default=_get_warehouse_id,
                                   string="Warehouse", required=False, )
    group_id = fields.Many2one(comodel_name="procurement.group",states=states_item_1 ,  copy=False, string="Procurement", required=False, )
    procurement_id = fields.Many2one(comodel_name="procurement.order",states=states_item_1 ,  copy=False, string="Procurement", required=False, )
    company_id = fields.Many2one('res.company', string='Company',states=states_item_1 ,  required=True, default=lambda self: self.env.user.company_id)
    # currency_id = fields.Many2one('res.currency', string='Currency', required=False, states=states_1,  default=lambda self: self.env.user.company_id.currency_id)





class project_component(models.Model):
    _name = 'project.component'
    _rec_name = 'name'
    _description = 'project.component'

    _order='state DESC'

    
    def unlink(self):

        if self.state =='confirm':

            raise UserError(_(
                'The operation cannot be completed:\nYou are trying to delete Component Confirmed.'))
        return super(project_component, self).unlink()

    
    @api.depends('item_id','product_id')
    def _compute_component_name(self):
        name=''
        if self.item_id and self.product_id:
            name = self.product_id.name+ "/"+self.item_id.name

        self.name=name


        return True



    @api.onchange('product_id')
    def _onchange_product_id(self):

        self.product_uom=self.product_id.uom_id.id


    
    def cp_component_confirm(self):
        if self.product_id and self.component_qty and self.component_qty >0:

            self.write({'state': 'confirm'})

        else:
            raise UserError(_('Error !Cannot Confirm The Item : Make Sure The Line Have Peoduct And QTY > 0 '))

        return True

    
    @api.depends('item_id', 'item_id.unit_id')
    def _compute_project_unit(self):
        project_id = False
        unit_id = False
        if self.item_id and self.item_id.unit_id and self.item_id.unit_id.project_id:
            if self.item_id.unit_id.project_id:
                project_id = self.item_id.unit_id.project_id.id
                unit_id = self.item_id.unit_id.id
        self.project_id = project_id
        self.unit_id = unit_id

        return True

    project_id = fields.Many2one(comodel_name="construction.project", compute="_compute_project_unit", store=True,
                                 string="Project", required=False, )
    unit_id = fields.Many2one(comodel_name="project.unit",compute="_compute_project_unit",store=True , string="Unit", required=False, )

    name = fields.Char(string="Component Name",compute="_compute_component_name",store=True, required=False, )
    item_id = fields.Many2one(comodel_name="project.item",    string="Item", required=True, )
    product_id = fields.Many2one(comodel_name="product.product",    string="Component Product", required=True, )
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    component_qty = fields.Float(string="QTY", default=1, required=True,  )
    component_cost = fields.Float(string="Component Cost", required=False,   )

    component_description = fields.Text(string="Component Description", required=False,   )
    state = fields.Selection(string="State", default='new' , selection=[('new', 'Draft'), ('confirm', 'Confirm'), ], required=False, )


    procurement_id = fields.Many2one(comodel_name="procurement.order",   copy=False, string="Procurement", required=False, )


    picking_id = fields.Many2one(comodel_name="stock.picking",   copy=False, string="Picking", required=False, )

    
    @api.depends('picking_id', 'picking_id.state')
    def _compute_picking_state(self):
        picking_state = ''
        if self.picking_id:
            picking_state = self.picking_id.state

        self.picking_state = picking_state
        return True

    picking_state = fields.Char(string="Picking State", compute="_compute_picking_state", store=True, required=False, )
