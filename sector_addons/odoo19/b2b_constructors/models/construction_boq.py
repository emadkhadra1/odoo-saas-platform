# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError



class ConstructionBOQ(models.Model):
    _name = "b2b.construction.boq"
    _inherit = ['mail.thread']
    _description = "جدول كميات المقاولات"

    STATING = [
        ("draft", "Draft"),
        ("cancel", "إلغاء"),
        ("wait_approve", "Wait Approve"),
        ("wait_assignment", "Assigned"),
        ("assigned", "تم"),
        ("refuse", "Refused"),
    ]
    # editable_states = {'draft': [('readonly', False)], 'wait_approve': [('readonly', False)], 'wait_assignment': [('readonly', False)]}
    # editable_states = {'draft': [('readonly', False)]}
    editable_states = {'draft': [('readonly', False)], 'wait_approve': [('readonly', False)]}

    name = fields.Char(string="عرض المقاول",readonly=True, states=editable_states)
    state = fields.Selection(STATING, string='الحالة', default="draft",readonly=True, states=editable_states, tracking=True)
    date_order = fields.Date(string="التاريخ", required=True,readonly=True, states=editable_states)
    construction_type_id = fields.Many2one('b2b.constrution.type', string='أنواع المقاولات',readonly=True, states=editable_states)
    project_id = fields.Many2one("construction.project", string='اسم المشروع',readonly=True, states=editable_states)
    indexation_ids = fields.One2many('b2b.indexation', 'purchase_order_id', string='بند جدول الكميات',readonly=True, states=editable_states)
    constructor_ids = fields.One2many('b2b.entrepreneurs', 'purchase_order_id', string='إسناد المقاول', states=editable_states)
    business_statement_domain_ids = fields.Many2many(comodel_name="b2b.business.items", relation="construction_business_statement_rel", column1="construction_id", column2="business_statement_id", string="نطاق بيان الأعمال", )
    total_cost = fields.Float(string="إجمالي التكلفة",  required=False, compute="_compute_total_cost_sell")
    total_sell = fields.Float(string="إجمالي البيع",  required=False, compute="_compute_total_cost_sell")

    
    @api.depends('indexation_ids')
    def _compute_total_cost_sell(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            rec.total_sell = sum([ind.total for ind in rec.indexation_ids])
            rec.total_cost = sum([ind.total_cost for ind in rec.indexation_ids])

    @api.onchange('indexation_ids')
    def _onchange_indexation_ids(self):
        for rec in self:
            indexes = [index.business_statement_id.id for index in rec.indexation_ids]
            rec.business_statement_domain_ids = [(6, 0, indexes)]

    def open_invoices(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        account_ids = []
        boq = self.env["b2b.progress.bill"].search([
            ("purchase_order_id", "=", self.id),
        ])

        for b in boq:
            if b.invoice_id:
                account_ids.append(b.invoice_id.id)

        result['domain'] = [('id', 'in', account_ids)]
        return result

    def open_qoutations(self):
        action = self.env.ref('b2b_constructors.b2b_progress_bill_action')
        result = action.read()[0]
        result['domain'] = [('purchase_order_id', '=', self.id)]
        return result

    
    def action_submit(self):
        for rec in self:
            rec.write({
                "state": "wait_approve",
            })

    
    def action_cancel(self):
        for rec in self:
            rec.write({
                "state": "cancel",
            })

    
    def action_set_draft(self):
        for rec in self:
            rec.write({
                "state": "draft",
            })
    
    def action_refused(self):
        for rec in self:
            rec.write({
                "state": "refuse",
            })

    
    def action_wait_assignment(self):
        env_construction_boq_wizard = self.env['b2b.entrepreneurs.wizard']
        default_consructor_id = self.env.user.company_id.partner_id.id
        construction_boq_wizard_vals = {'consructor_id': default_consructor_id}

        for rec in self:
            add_constructor_lines = []
            for index in rec.indexation_ids:
                add_constructor_lines.append((0, 0, {'indexation_id': index.id, 'price': index.category,
                                                     'percent': index.required_quantity, 'purchase_order_id': rec.id,
                                                     'consructor_id': default_consructor_id}))
            construction_boq_wizard_vals.update({'item_ids': add_constructor_lines, 'purchase_order_id': rec.id})
            wizard_obj = env_construction_boq_wizard.create(construction_boq_wizard_vals)
            if wizard_obj:
                wizard_obj.action_assign()

            rec.write({
                "state": "wait_assignment",
            })
            current_project = self.env['construction.project'].search([('id', '=', rec.project_id.id)],
                                                                      limit=1)
            if current_project:
                bom = {
                    'bom_id': rec.id,
                    'boq_name': rec.name,
                    'boq_type': rec.construction_type_id.name,
                    'boq_date': rec.date_order,
                    'boq_total_cost': rec.total_cost,
                    'boq_total_sell': rec.total_sell,
                    'construction_project_id': current_project.id,

                }
                print('--------------', bom)
                current_project.boq_line_ids.sudo().create(bom)

    
    def action_assigned(self):
        for rec in self:
            if not rec.constructor_ids:
                raise ValidationError("Please, Assign Constructors first!")
            else:
                rec.write({
                    "state": "assigned",
                })

    
    def action_print(self):
        for rec in self:
            pass

    
    def action_open_assign_form(self):
        domain = []
        context = {}
        for rec in self:
            context = dict(self.env.context or {})
            context['active_id'] = rec.id
        return {
            'name': _('????????? ????????'),
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'b2b.entrepreneurs.wizard',
            'view_id': self.env.ref('b2b_constructors.view_assign_constructor_wizard_form').id,
            'target': 'new',
            'domain': domain,
            'context': context,
        }
    
    
class construction_receive_order(models.Model):
    _inherit = 'construction.receive.order'

    boq_id = fields.Many2one(comodel_name="b2b.construction.boq", string="جدول كميات المقاولات")
    business_statement_ids = fields.Many2many(comodel_name="b2b.business.items")

    @api.onchange('boq_id')
    def onchange_boq_id(self):
        self.business_statement_ids = False
        self.business_statement_ids = [[4, cl.id, False] for cl in self.boq_id.indexation_ids.mapped('business_statement_id')]
        
    def confirm(self):
        lines = []
        interal_transfer = {}
        for line in self.receive_order_ids:
            print(line.qty_available, line.qty, line.accept)
            if line.qty_available < line.qty:
                raise UserError(_('???! ?????? ??? ????? ????????.'))
            if not line.accept:
                raise ValidationError(_('???! ???? ??? ??? ?????.'))

                # raise UserError(_('???! ???? ??? ??? ?????.'))
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
                                'business_item_id': line.business_statement_id.id if line.business_statement_id else False,
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
                        #     raise UserError(_('???! ?? ???? ?????? ???????.'))
                        # print origin
                        # print line
                    else:
                        action='line_not_accept'
                        raise UserError(_('???! ???? ??? ??? ?????.'))

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


class construction_receive_order_line(models.Model):
    _inherit = 'construction.receive.order.line'

    business_statement_id = fields.Many2one("b2b.business.items", string="بيان الأعمال", required=True)

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
                'business_item_id': one.business_statement_id.id if one.business_statement_id else False,
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

