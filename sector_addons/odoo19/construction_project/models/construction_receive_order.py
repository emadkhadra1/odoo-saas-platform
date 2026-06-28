# -*- coding: utf-8 -*-
import json
from lxml import etree
from odoo import models, fields, api, _,exceptions
# from odoo.osv.orm import setup_modifiers
# from openerp.tools.translate import _
# from openerp import models, fields, api
# from openerp.exceptions import Warning
from datetime import date

from datetime import datetime ,date

# from reportlab.graphics.widgetbase import Face
from odoo.exceptions import UserError, ValidationError


class construction_receive_order(models.Model):
    _name = 'construction.receive.order'
    _rec_name = 'name'
    _description = 'construction_receive_order'
    _inherit = ['mail.thread',]


    
    def update_message_follower(self):
        user_obj = self.env['res.users']
        all_users_data = user_obj.search([])
        for one_user in all_users_data:
            if one_user.has_group('construction_project.receive_order_manager_group'):
                self.message_subscribe([one_user.partner_id.id])


        user_id = self.user_id
        if user_id  and user_id.partner_id:
            self.message_subscribe([user_id.partner_id.id])

        return True

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
    #                     submenu=False):
    #     res = super(construction_receive_order, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar,
    #         submenu=submenu)
    #
    #     receive_order_manager_group = self.env.user.has_group('construction_project.receive_order_manager_group')
    #     readonly_order_qty = "0"
    #     if receive_order_manager_group:
    #         readonly_order_qty="1"
    #     if view_type == 'tree':
    #         iiii=''
    #     if view_type == 'form' :
    #         doc = etree.XML(res['arch'])
    #
    #         for node in  doc.xpath("//field[@name='receive_order_ids']"):
    #
    #             tree=res['fields']['receive_order_ids']['views']['tree']
    #
    #             for chiled in node.xpath("/tree//field[@name='order_qty']"):
    #                 te=''
    #             for chiled in node.xpath("/tree"):
    #                 te=''
    #             for chiled in node.xpath("//tree"):
    #                 te=''
    #             for chiled in node.xpath("//tree//field[@name='order_qty']"):
    #                 te=''
    #             for chiled in  node.xpath("//field[@name='order_qty']"):
    #                 ci=''
    #             # node.set('readonly', '0')
    #             # node.set('help', 'You Can Edit Now')
    #             # setup_modifiers(node, res['fields']['overtime_structure_id'])
    #         res['arch'] = etree.tostring(doc)
    #     return res



    
    def unlink(self):
        if self.state == 'done':
            raise UserError(_('You cannot delete .'))
        return super(construction_receive_order, self).unlink()

    def _get_date_now(self):
        res=datetime.now().date()
        return res


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
            print("quant_data ##############################", quant_data)
            for quant in quant_data:
                res+=quant.quantity


        return res

    
    def confirm(self):
        lines = []
        interal_transfer = {}
        for line in self.receive_order_ids:
            print(line.qty_available, line.qty, line.accept)
            if line.qty_available < line.qty:
                raise UserError(_('Error ! QTY Not Available To Accepted.'))
            if not line.accept:
                raise ValidationError(_('Error ! You Have Line Not Accepted.'))

                # raise UserError(_('Error ! You Have Line Not Accepted.'))
                # print 'Error ! You Have Line Not Accepted.'
        picking_id = False
        if self.project_id and self.project_id.partner_id:
            partner_id = self.project_id.partner_id.id

        else:
            partner_id = False
        if self.warehouse_id:
            warehouse_id = self.warehouse_id
        else:
            company_id = self.env.user.company_id.id
            warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)], )
            warehouse_id = warehouse_ids[0]

        if self.warehouse_id:
            print("1")

            print("location_id", self.location_id.name)
            print("location_dest_id", self.location_dest_id.name)
            print("picking_type_id", self.picking_type_id.name)

            if self.location_id and self.location_dest_id and self.picking_type_id:
                print("2")

                print('ready to picking')
                group_id = self.env['procurement.group'].create({

                    'name': "RO#" + str(self.id),
                    'move_type': 'direct',
                    'partner_id': partner_id,
                })
                rule_id = False
                self.group_id = group_id.id
                line_ids=[]
                for line in self.receive_order_ids:
                    if line.accept:
                        print("3")
                        all_locations = []
                        my_qty = self.get_my_qty(line.product_id, self.location_id, all_locations)
                        print("my_qty ###################", my_qty)
                        print("line.qty ###################", line.qty)
                        print("______________my_qty__________")
                        print(all_locations)
                        print(self.location_id)
                        print(my_qty)
                        if my_qty <= 0:
                            # if line.product_id.qty_available <= 0:
                            raise UserError(_('Error ! Not Available QTY ' + line.product_id.name + '  ' + str(
                                str(my_qty)) + ' In Location ' + self.location_id.name))
                        # if line.qty > line.product_id.qty_available:
                        if line.qty > my_qty:
                            print("saber")
                            raise UserError(_(
                                'Error ! Cannot Confirm The Component (' + line.product_id.name + ')' + str(
                                    line.qty) + ' :     Available ' + str(
                                    my_qty) + ' In Location ' + self.location_id.name))
                        # print 'The Component (' + line.product_id.name + ')' + str(
                        #             line.qty) + ' : QTY Not Available  . Only Available ' + str(
                        #             my_qty) + ' In Location ' + self.location_id.name
                        else:
                            print("ahmed")
                            # procurement_id = self.env['stock.picking'].create(
                            #     {'product_id': line.product_id.id,
                            #      'product_qty': line.qty,
                            #      'product_uom': line.product_id.uom_id.id,
                            #      'name':   "ROL#" + str(line.id),
                            #      'origin': origin,
                            #      'warehouse_id': warehouse_id.id,
                            #      'location_id': self.location_dest_id.id,
                            #      'company_id': self.company_id.id,
                            #      'group_id': group_id.id,
                            #      'rule_id': rule_id,
                            #      'picking_type_id': self.picking_type_id.id,
                            #      'partner_dest_id': partner_id,
                            #      'date_planned': self.date,
                            #      'location_dest_id': self.location_dest_id.id,
                            #      })
                            # print("procurement_id @@@@@@@@@@@@@@@@@@@", procurement_id)
                            # line_ids.append(line.id)

                            lines.append((0, 0, {
                                'name': "ROL#" + str(line.id),
                                'product_id': line.product_id.id,
                                'product_uom': line.product_id.uom_id.id,
                                'product_uom_qty': line.qty2,
                                'location_id': self.location_id.id,
                                'location_dest_id': self.location_dest_id.id,
                                'analytic_distribution': {self.project_id.analytic_account_id.id: 100} if self.project_id.analytic_account_id else False,
                                 }))
                            interal_transfer = {
                                # 'request_id': self.id,
                                'partner_id': self.project_id.partner_id.id,
                                # 'origin': "ROL#" + str(self.id),
                                'picking_type_id': self.project_id.picking_type_id.id,
                                'location_id': self.project_id.location_id.id,
                                'location_dest_id': self.project_id.location_dest_id.id,
                                'receive_order_id_ref': self.id,
                                'origin': self.name,
                                'move_ids_without_package': lines,
                            }

                        # if procurement_id and procurement_id.state!='done':
                        #     error=''
                        #     raise UserError(_('Error ! procurement cannot confirm'))
                        # print origin
                        # print line
                    else:
                        action='line_not_accept'
                        raise UserError(_('Error ! You Have Line Not Accepted.'))

                # print "group_id",group_id
                # print "line_ids",line_ids
                # print "partner_id",partner_id
                if group_id and line_ids and partner_id:
                    print("4")
                    i=0
                    picking_data = self.env['stock.picking'].search([('group_id', '=', group_id.id)], )
                    for picking in picking_data:
                        lineid = line_ids[i]
                        i+=1
                        picking_id = picking
                        picking_id.write({'partner_id': partner_id, 'receive_order_line_id': lineid})
                        picking_id.action_confirm()
                        picking_id.action_assign()
                        picking_id.force_assign()
                        picking_id.do_transfer()
                        inventory_value = 0
                        valuations = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', picking_id.move_lines.ids)])
                        for quant in valuations:
                            inventory_value += quant.value
                        # print "inventory_value"
                        # print inventory_value
                        line.write({'cost': inventory_value})
                        # get cost now


                        line.write({'picking_id': picking_id.id})

        else:
            print("5")
            msg = ''
            if not warehouse_id:
                msg += '\n - No warehouse assigned to this user '
            if not self.order_type:
                msg += '\n - No data in order_type '
            if not self.order_line:
                msg += '\n - No data in order_line '
            raise UserError('Some Data Is Missing To Cerate Stock Move' + msg)

        self.state = 'done'
        self.env['stock.picking'].create(interal_transfer)
        stock_picking_object = self.env['stock.picking'].search([('receive_order_id_ref', '=', self.id)], limit=1)
        self.stock_picking_ref = stock_picking_object.id

        return True

    
    @api.depends('receive_order_ids','receive_order_ids.price','receive_order_ids.cost')
    def _compute_total(self):
        total_amount=0
        # total_cost=0
        if self.receive_order_ids:
            for line in self.receive_order_ids:
                total_amount+=line.price
                # total_cost+=line.cost
        self.total_amount=total_amount
        # self.total_cost=total_cost
        return True


    @api.onchange('receive_order_user_ids')
    def _compute_unit_cost_total(self):
        total = sum(self.receive_order_user_ids.mapped('price'))
        self.total_cost = total



    # @api.depends('receive_order_user_ids')
    # def _compute_unit_cost_total(self):
    #     total = 0.0
    #     for rec in self.receive_order_user_ids:
    #         total = sum(rec.mapped('unit_cost'))
    #     print("unit_cost_total", total)
    #     self.total_cost = total
    #     # total = 0.0
    #     # for rec in self.receive_order_user_ids:
    #     #     total += rec.unit_cost
    #     # print("total", total)
    #     # self.total_cost = total

    # 
    # def write(self, vals):
    #     res = super(construction_receive_order, self).write(vals)
    #     self.update_message_follower()
    #     return res

    @api.model
    def create(self, vals):
        # if vals.get('name', 'New') == 'New' and self.env.user.company_id.type == 'maka':
        #     # print('iam in rental.sequence')
        #     vals['name'] = (self.env['ir.sequence'].next_by_code('construction.receive.order.maka')) or 'New'
        # if vals.get('name', 'New') == 'New' and self.env.user.company_id.type == 'madina':
            # print('iam in rental.sequence')
        vals['name'] = (self.env['ir.sequence'].next_by_code('construction.receive.order.madina')) or 'New'
        res = super(construction_receive_order, self).create(vals)
        # res.update_message_follower()
        return res

    order_number = fields.Char(string="رقم أذن الصرف", required=False, readonly=True)

    total_amount = fields.Float(string="Total Amount", tracking=True,compute="_compute_total", store=True, required=False,)

    total_cost = fields.Float(string="Total Cost", required=False, )

    name = fields.Char(string="Serial",required=False,tracking=True,)
    name2 = fields.Char(string="Name", required=False, readonly=True)
    project_id = fields.Many2one(comodel_name="construction.project", tracking=True,  string="Project", required=True, )
    location_id = fields.Many2one('stock.location', 'Source Location', related="project_id.location_id",
                                  store=True, required=False)
    picking_type_id = fields.Many2one('stock.picking.type',related="project_id.picking_type_id" ,store=True,  string='Picking Type')

    location_dest_id = fields.Many2one('stock.location', 'Destination Location',
                                       related="project_id.location_dest_id", store=True, required=False)

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", related="project_id.warehouse_id",
                                   store=True, string="Warehouse", )

    company_id = fields.Many2one('res.company', string='Company', related="project_id.company_id", store=True, )


    date = fields.Date(string="Date",default=_get_date_now , tracking=True,required=False, )
    delegate = fields.Char(string="Delegate", required=False, )
    receive_order_ids = fields.One2many(comodel_name="construction.receive.order.line", inverse_name="receive_order_id", string="Receive Order Lines", required=False, )
    receive_order_user_ids = fields.One2many(comodel_name="construction.receive.order.line", inverse_name="receive_order_id", string="Receive Order Lines", required=False, )
    state = fields.Selection(string="State",default='new', tracking=True,selection=[('new', 'New'), ('done', 'Approved'),('delivered', 'Delivered'), ], required=False, )


    group_id = fields.Many2one(comodel_name="procurement.group",   copy=False, string="Procurement",
                               required=False, )
    # procurement_id = fields.Many2one(comodel_name="procurement.order",  copy=False,
    #                                  string="Procurement", required=False, )


    user_id = fields.Many2one('res.users', string='Order By',tracking=True, index=True,  default=lambda self: self.env.uid)

    reason = fields.Text(string="Reason",tracking=True, required=False, )

    notes = fields.Text(string="Notes",tracking=True, required=False, )

    stock_picking_ref = fields.Many2one(comodel_name="stock.picking", string="", required=False, )


class construction_receive_order_line(models.Model):
    _name = 'construction.receive.order.line'
    _rec_name = 'name'
    _description = 'construction_receive_order_line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(construction_receive_order_line, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

        receive_order_manager_group = self.env.user.has_group('construction_project.receive_order_manager_group')
        readonly_order_qty = "0"
        help = "Can edit"
        if receive_order_manager_group:
            readonly_order_qty = "1"
            help = "Can Not edit"

        if view_type in ['tree','form'] :
            aaa=''
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='order_qty']")
            for node in nodes:
                node.set('readonly', readonly_order_qty)
                node.set('help', help)
                # setup_modifiers(node, res['fields']['order_qty'])
            res['arch'] = etree.tostring(doc)


        return res

    @api.onchange('receive_order_id')
    def _onchange_receive_order_id(self):
        if self.delay_order and self.receive_order_id:
            self.delay_order=False
    #
    # 
    # def write(self, vals):
    #     if self.delay_order and self.receive_order_id  :
    #         self.location_dest_id.write({'delay_order': False})
    #
    #     line = super(construction_receive_order_line, self).write(vals)
    #
    #     return line


    
    @api.constrains('order_qty','unit_price')
    def _onchange_order_qty_unit_price(self):
        for rec in self:
            if not rec.order_qty:
                raise ValidationError(_('خطاء! أدخل قيمة الكمية QTY'))
            # if rec.unit_price==0.0:
            #     raise Warning(_('خطاء! أدخل سعر بيع الوحدة '))



    # @api.depends('product_id')
    # def _onchange_product_id(self):
    #     print("000000000000000000000000000000000000000000000")
    #     unit_cost = 0
    #     # self.unit_price = 0
    #     # product_object = self.env['product.template'].search([()])
    #     for rec in self:
    #         if rec.product_id:
    #             rec.unit_cost = rec.product_id.seller_ids.price
    #         else:
    #             rec.unit_cost = 0.0



        # self.unit_price = self.product_id.list_price
        # self.qty_available = self.product_id.qty_available
        # for one in self:
        #     one.write({'qty_available':self.product_id.qty_available})
        # if self.product_id:
        #
        #     self._cr.execute("  SELECT purchase_order_line.price_unit FROM purchase_order_line"
        #                      " INNER JOIN  purchase_order ON  purchase_order_line.order_id =  purchase_order.id "
        #                      "INNER JOIN stock_picking ON purchase_order.name = stock_picking.origin"
        #                      " WHERE stock_picking.state = 'done' AND purchase_order_line.product_id"
        #                      " = %s ORDER BY stock_picking.date_done DESC LIMIT 1 ", self.product_id.id)
        #     unit_cost = self._cr.fetchall()
        # stock_picking_obj=self.env['stock.picking']
        # pol_obj=self.env['purchase.order.line']
        # pol_data=pol_obj.search([('product_id','=',self.product_id.id),('state','=','purchase')] ,  order='date_planned asc' )
        #
        # for one_pol in pol_data:
        #     origin=one_pol.order_id.name
        #     stock_picking_data = stock_picking_obj.search([('origin', '=', origin), ('state', '=', 'done')])
        #
        #     if stock_picking_data:
        #         unit_cost=one_pol.price_unit

        # self.unit_cost = unit_cost



    
    @api.depends('product_id', 'qty', 'unit_cost')
    def compute_price(self):
        for rec in self:
            if rec.product_id and rec.qty:
                rec.price = rec.unit_cost * rec.qty
            else:
                rec.price = 0
        return True

    @api.onchange('product_id')
    def onchange_product_unit_cost(self):
        for rec in self:
            rec.unit_cost = rec.product_id.standard_price
        return {'domain': {'product_id': [('constration_product', '=', False)]}}


    @api.onchange('order_qty')
    def onchange_order_qty(self):
        if self.order_qty:
            self.qty = self.order_qty
            self.qty2 = self.order_qty


    #
    # @api.onchange('qty')
    # def onchange_qty(self):
    #     if self.qty:
    #         self.qty_user = self.qty
    
    @api.depends('product_id')
    def _compute_qty(self):
        for rec in self:
            unit_cost = 0
            if rec.qty:
                rec.qty2 = rec.qty
        return True



    # 
    # @api.depends('product_id')
    # def _compute_cost(self):
    #     unit_cost = 0
    #     if self.product_id:
    #
    #         self._cr.execute("  SELECT purchase_order_line.price_unit FROM purchase_order_line"
    #                          " INNER JOIN  purchase_order ON  purchase_order_line.order_id =  purchase_order.id "
    #                          "INNER JOIN stock_picking ON purchase_order.name = stock_picking.origin"
    #                          " WHERE stock_picking.state = 'done' AND purchase_order_line.product_id"
    #                          " = %d ORDER BY stock_picking.date_done DESC LIMIT 1 " % self.product_id.id)
    #
    #         res = self._cr.fetchone()
    #         # print "RES"
    #         # print res
    #         if res:
    #             unit_cost = res[0]
    #     self.unit_cost = unit_cost
    #     #zakaria 20170731
    #     self.unit_cost =0
    #     return True
    
    def accept_line(self):
        # print 'accept_line'
        # print self.qty_available
        # print self.qty
        if self.qty_available < self.qty:
            # print 'Error ! QTY Not Available To Accepted.'
            raise UserError(_('Error ! QTY Not Available To Accepted.'))

        self.accept = True
        self.delay_order = False
        return True
    
    def make_delay_line(self):
        for one in self:
            # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(one.receive_order_id)
            print(one.receive_order_id.name)
            # print(self._context)
            # print(self._context.get('active_id'))
            # one.receive_order_id = one.receive_order_id.id
            one.accept = False
            one.delay_order=True
        return True

    @api.depends('order_qty', 'qty_available', 'qty')
    def _compute_qty_state(self):
        for rec in self:
            if rec.order_qty > rec.qty_available:
                rec.qty_state = "red"
            elif rec.qty <= rec.order_qty:
                rec.qty_state = "green"
        return True

    def make_purchase_order(self):
        purchase = self.env['purchase.order']
        purchase_line = self.env['purchase.order.line']
        for one in self:
            purchase_id = purchase.create({
                'partner_id': one.project_id.partner_id.id,
                'date_planned': datetime.now(),
                'state': 'draft',
                'origin':one.receive_order_id.name,
            })
            purchase_line_id = purchase_line.create({
                'product_id': one.product_id.id,
                'product_qty': one.qty,
                'name': one.name or one.product_id.name,
                'product_uom': one.product_id.uom_po_id.id,
                'price_unit': 0,
                'order_id': purchase_id.id,
                'date_planned': datetime.now(),
            })

            one.write({'purchase_line_id': purchase_line_id.id})
            return {
                'type': 'ir.actions.act_window',
                'name': 'purchase.purchase_order_form',
                'res_model': 'purchase.order',
                'res_id': purchase_id.id,
                'view_mode': 'form',
                'target': 'self',
            }

    accept = fields.Boolean(string="Accept",  )
    delay_order = fields.Boolean(string="Delay",  )
    purchase_line_id = fields.Many2one(comodel_name="purchase.order.line",   copy=False, string="PO Line", required=False, )
    picking_id = fields.Many2one(comodel_name="stock.picking",   copy=False, string="Picking", required=False, )

    # procurement_id = fields.Many2one(comodel_name="procurement.order",   copy=False, string="Procurement", required=False, )

    name = fields.Char(string="Name", required=False,)
    receive_order_id = fields.Many2one(comodel_name="construction.receive.order",   string="Receive Order", required=False, )
    project_id = fields.Many2one(comodel_name="construction.project", related="receive_order_id.project_id",sotre=True,  string="Project", required=False, )
    order_number = fields.Char(string="رقم أذن الصرف" ,related="receive_order_id.order_number")

    product_category_id = fields.Many2one(comodel_name="product.category",    string="Product Category", required=False)
    product_id = fields.Many2one(comodel_name="product.product",   readonly=True, states={'new': [('readonly', False)]},  string="Product", required=True,
                                 domain=[('constration_product','=', False)])
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id',store=True,readonly=True)
    qty_available = fields.Float(string="QTY Available", related="product_id.qty_available",store=True, required=False, )

    order_qty = fields.Float(string="QTY",digits=(16,3),  required=False, )
    # qty_user = fields.Float(string="Approved QTY",default=1,  required=True, )
    qty = fields.Float(string="Approved QTY",default=1,  required=True, )
    qty2 = fields.Float(string="Approved QTY",default=1,compute="_compute_qty",  required=True, )
    unit_price = fields.Float(string="Uint Price", default=0, required=True, )
    price = fields.Float(string="Price",compute="compute_price",store=True, required=False, )
    unit_cost = fields.Float(string="Last Uint Cost",  required=False)
    cost = fields.Float(string="Cost",   required=False, )
    #zakaria strat
    state = fields.Selection(string="State",default='new', related="receive_order_id.state",tracking=True,selection=[('new', 'New'), ('done', 'Approved'),('delivered', 'Delivered'), ], required=False, readonly=True, copy=False, index=True, )
    #zakaria end

    location_id = fields.Many2one('stock.location', 'Source Location', related="receive_order_id.location_id",
                                  store=True, required=False)
    picking_type_id = fields.Many2one('stock.picking.type', related="receive_order_id.picking_type_id", store=True,
                                      string='Picking Type')
    location_dest_id = fields.Many2one('stock.location', 'Destination Location',
                                       related="receive_order_id.location_dest_id", store=True, required=False)

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", related="receive_order_id.warehouse_id",
                                   store=True, string="Warehouse", )

    company_id = fields.Many2one('res.company', string='Company', related="receive_order_id.company_id",
                                 store=True, )

    qty_state = fields.Char(string="Qty State", compute="_compute_qty_state",store=True,  required=False, )

    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('construction.receive.order.line.madina')) or 'New'
        res = super(construction_receive_order_line, self).create(vals)
        # res.update_message_follower()
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('state')
    def _compute_change_receive_order(self):
        change_receive_order = "Waiting"
        if (self.receive_order_line_id or self.receive_order_id_ref) and self.state and self.state =='done':
            ok='change state and git cost line'
            inventory_value = 0
            inv_qty = 0
            unit_cost = 0
            valuations = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', self.move_lines.ids)])
            for quant in valuations:
                inventory_value += quant.value
                inv_qty += quant.quantity
                    # print ">>quant.inventory_value= ",quant.inventory_value
            # print "inventory_value/quant.qty>>>>>>>>",inventory_value/quant.qty
            # print "inventory_value"
            # print inventory_value
            if inv_qty:
                unit_cost = inventory_value / inv_qty
            self.receive_order_line_id.write({'cost': inventory_value,'unit_cost': unit_cost})
            change_receive_order ="Done"
            #zakaria start
            receive_order = self.env['construction.receive.order']
            self.receive_order_id_ref.write({'state': 'delivered'})
            #zakaria end
        self.change_receive_order = change_receive_order
        return True

    change_receive_order = fields.Char(string="change_receive_order",compute="_compute_change_receive_order", required=False, )
    receive_order_line_id = fields.Many2one(comodel_name="construction.receive.order.line",    string="Order Line", required=False, )
    #zakaria start
    receive_order_id = fields.Many2one(comodel_name="construction.receive.order",related="receive_order_line_id.receive_order_id",  string="Receive Order", required=False, )

    receive_order_id_ref = fields.Many2one(comodel_name="construction.receive.order", string="", required=False, )
    #zakaria end
    project_id = fields.Many2one(comodel_name="construction.project", related="receive_order_line_id.project_id",store=True,   string="Project", required=False, )
    order_number = fields.Char(string="رقم أذن الصرف" ,related="receive_order_line_id.order_number")


    
    def action_done(self):
        print("ahmed saber &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print("receive_order_id", self.receive_order_id)
        print("receive_order_id_ref", self.receive_order_id_ref)

        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                    'picking_type_id': pick.picking_type_id.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move = new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves._action_done()
        self.write({'date_done': fields.Datetime.now()})
        if self.receive_order_id_ref:
            print("self.receive_order_id_ref.state", self.receive_order_id_ref.state)
            self.receive_order_id_ref.write({'state': 'delivered'})
            print("self.receive_order_id_ref.state", self.receive_order_id_ref.state)
            self.receive_order_id_ref.state = 'delivered'
            print("self.receive_order_id_ref.state", self.receive_order_id_ref.state)
        return True


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    project_id = fields.Many2one('construction.project', string="المشروع")


class StockMove(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one('construction.project',related="picking_id.project_id", string="المشروع")