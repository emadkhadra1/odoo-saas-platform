# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
# from openerp.osv.orm import setup_modifiers
# from openerp.tools.translate import _
# from openerp import models, fields, api
# from openerp.exceptions import Warning
from datetime import date

from datetime import datetime ,date

# from reportlab.graphics.widgetbase import Face
from odoo.exceptions import UserError, ValidationError


states_item_1 = {'new': [('readonly', False)],'confirm': [('readonly', True)]}

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
        for rec in self:
            name = ''
            if rec.unit_id and rec.product_id:
                name = "%s/%s" % (rec.product_id.name, rec.unit_id.name)
            rec.name = name
        return True

    
    @api.depends('project_component_ids' ,'project_component_ids.component_cost' )
    def _compute_total_item_cost(self):
        for rec in self:
            rec.total_item_cost = sum(rec.project_component_ids.mapped('component_cost'))
        return True

    
    @api.depends('item_qty' ,'total_item_cost' )
    def _compute_item_cost(self):
        for rec in self:
            item_cost = 0
            if rec.item_qty and rec.total_item_cost:
                item_cost = rec.total_item_cost / rec.item_qty
            rec.item_cost = item_cost
        return True

    
    def cp_item_confirm(self):
        if self.project_component_ids:
            if self.item_qty >0:
                self.action_stock_move()
                for line in self.project_component_ids:
                    line.cp_component_confirm()
                self.state='confirm'
            else:
                raise UserError(_('خطأ! لا يمكن اعتماد البند: يجب أن تكون الكمية أكبر من صفر.'))

        else:

            raise UserError(_('خطأ! لا يمكن اعتماد البند: تأكد من وجود مكون واحد على الأقل.'))

        return True

    def get_all_location(self,location_id,all_locations):
        location_obj=self.env['stock.location']
        all_locations.append(location_id)
        location_data=location_obj.search([('location_id','=',location_id)] )
        for one in location_data:
            self.get_all_location(one.id,all_locations)

        return all_locations
    def get_my_qty(self,product_id,location_id,all_locations):
        res=0

        all_locations=self.get_all_location(location_id.id,all_locations)
        quant_obj=self.env['stock.quant']
        if all_locations:
            quant_data=quant_obj.search([('product_id','=',product_id.id),('location_id','in',all_locations)] )
            for quant in quant_data:
                res+=quant.qty


        return res
    
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
                    all_locations=[]
                    my_qty=self.get_my_qty(line.product_id,self.location_id,all_locations)
                    # print "______________my_qty__________"
                    # print all_locations
                    # print self.location_id
                    # print my_qty
                    if my_qty<=0:
                    # if line.product_id.qty_available <= 0:
                        raise UserError(_('Error ! Not Available QTY ' + line.product_id.name + '  ' + str(
                            str(my_qty)) + ' In Location '+ self.location_id.name))
                    # if line.component_qty > line.product_id.qty_available:
                    if line.component_qty >my_qty:
                        raise UserError(_('Error ! Cannot Confirm The Component ('+line.product_id.name+')'+str(line.component_qty)+' : QTY Not Available  . Only Available '+str(my_qty)+ ' In Location '+ self.location_id.name))

                    origin = "CPC#" + str(line.id)
                    # procurement_id=self.env['procurement.order'].create(
                    #             {'product_id': line.product_id.id,
                    #                           'product_qty': line.component_qty,
                    #                           'product_uom': line.product_uom.id,
                    #                           'name': "CPL:" +line.name or "CPL#" + str(line.id),
                    #                           'origin': origin,
                    #                          'warehouse_id': warehouse_id.id,
                    #                           'location_id': self.location_dest_id.id,
                    #                           'company_id': self.company_id.id,
                    #                           'group_id': group_id.id,
                    #                           'rule_id':rule_id,
                    #                           'partner_dest_id':partner_id,
                    #                           # 'location_dest_id': self.location_dest_id.id,
                    #                               })


                    # if procurement_id:

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


                        # line.write({'procurement_id':procurement_id.id,'picking_id':picking_id.id})
                        line.write({'picking_id':picking_id.id})
                    # print origin
                    # print line

        else:
            msg = ''
            if not warehouse_id:
                msg += '\n - No warehouse assigned to this user '
            # if not self.order_type:
            #     msg += '\n - No data in order_type '
            # if not self.order_line:
            #     msg += '\n - No data in order_line '
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
        for rec in self:
            rec.picking_state = rec.picking_id.state if rec.picking_id else ''
        return True





        # self.update(values)

    
    @api.depends('unit_id','warehouse_id')
    def _compute_project_id(self):
        for rec in self:
            rec.project_id = rec.unit_id.project_id.id if rec.unit_id and rec.unit_id.project_id else False

        # if self.unit_id and self.unit_id.project_id and self.unit_id.project_id.partner_id:
        #     self.location_dest_id = self.unit_id.project_id.partner_id.property_stock_customer.id


        # if self.warehouse_id and self.warehouse_id.out_type_id:
        #     self.picking_type_id = self.warehouse_id.out_type_id.id
        #     if self.warehouse_id.out_type_id.default_location_src_id:
        #         self.location_id=self.warehouse_id.out_type_id.default_location_src_id.id

        return True
    unit_id = fields.Many2one(comodel_name="project.unit",states=states_item_1 ,  string="Unit", required=True, )

    def _get_date_now(self):
        res=datetime.now().date()
        return res

    date = fields.Date(string="Date",default=_get_date_now , required=True, )

    project_id = fields.Many2one(comodel_name="construction.project", compute="_compute_project_id",store=True,  string="Project", required=False, )

    location_id = fields.Many2one('stock.location', 'Source Location',related="unit_id.project_id.location_id",store=True,  required=False)

    location_dest_id = fields.Many2one('stock.location', 'Destination Location',related="unit_id.project_id.location_dest_id",store=True ,  required=False)

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse",related="unit_id.project_id.warehouse_id",store=True, string="المستودع",  )

    company_id = fields.Many2one('res.company', string='Company',related="unit_id.project_id.company_id",store=True,  )

    picking_type_id = fields.Many2one('stock.picking.type',related="unit_id.project_id.picking_type_id" ,store=True,  string='Picking Type')

    name = fields.Char(string="Unit Name",compute="_compute_item_name",store=True, required=False, )
    product_id = fields.Many2one(comodel_name="product.product",states=states_item_1 ,  string="Item Product", required=True, )
    product_uom = fields.Many2one('uom.uom',related="product_id.uom_id",store=True, string='Unit of Measure', required=False)
    item_description = fields.Text(string="Item Description",states=states_item_1 ,  required=False, )
    item_qty = fields.Float(string="Item QTY",default=1,  required=True,states=states_item_1 ,  )


    project_component_ids = fields.One2many(comodel_name="project.component", states=states_item_1 , inverse_name="item_id",
                                       string="Project Component Lines", required=False, )
    state = fields.Selection(string="State", default='new' , selection=[('new', 'Draft'), ('confirm', 'Confirm'), ], required=False, )



    total_item_cost = fields.Float(string="Total Item Cost",compute="_compute_total_item_cost",store=True,  required=False, )
    item_cost = fields.Float(string="Item Cost",compute="_compute_item_cost",store=True,  required=False, )


    group_id = fields.Many2one(comodel_name="procurement.group",states=states_item_1 ,  copy=False, string="Procurement", required=False, )
    # procurement_id = fields.Many2one(comodel_name="procurement.order",states=states_item_1 ,  copy=False, string="Procurement", required=False, )
    # currency_id = fields.Many2one('res.currency', string='Currency', required=False, states=states_1,  default=lambda self: self.env.user.company_id.currency_id)



    process_id = fields.Many2one(comodel_name="construction.process", string="مرحلة التنفيذ", required=False, )


class construction_process(models.Model):
    _name = 'construction.process'
    _rec_name = 'name'
    _description = 'construction process'

    name = fields.Char(string="مرحلة التنفيذ", required=True, )
