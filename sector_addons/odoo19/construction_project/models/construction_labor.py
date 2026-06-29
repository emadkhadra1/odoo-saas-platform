from odoo.tools.translate import _
from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


class construction_labor(models.Model):
    _name = 'construction.labor'
    _rec_name = 'name'
    _description = 'construction_labor'
    _inherit = ['mail.thread', ]

    
    def unlink(self):
        if self.state == 'done':
            raise UserError(_('You cannot delete .'))
        return super(construction_labor, self).unlink()

    def _get_date_now(self):
        res = datetime.now().date()
        return res

    
    def confirm(self):
        self.create_account_move()
        self.state = 'done'
        return True

    
    @api.depends('line_ids', 'line_ids.cost')
    def _compute_total(self):
        for rec in self:
            total_cost = sum(rec.line_ids.mapped('cost'))
            rec.total_cost = total_cost
            rec.total_amount = total_cost
        return True

    total_amount = fields.Float(string="Total Amount", tracking=True, compute="_compute_total", store=True,
                                required=False, )
    total_cost = fields.Float(string="Total Cost", tracking=True, compute="_compute_total", store=True,
                              required=False, )
    name = fields.Char(string="Serial", tracking=True, required=False, )
    project_id = fields.Many2one(comodel_name="construction.project", tracking=True, string="Project",
                                 required=True, )
    date = fields.Date(string="Date", default=_get_date_now, tracking=True, required=False, )
    state = fields.Selection(string="State", default='new', tracking=True,
                             selection=[('new', 'New'), ('done', 'Done'), ],
                             required=False, )
    line_ids = fields.One2many(comodel_name="construction.labor.line", inverse_name="order_labor_id",
                               string="Labor Lines", required=False, )
    employment = fields.Selection(string="Employment", default='in', tracking=True,
                                  selection=[('in', 'Company Employment '), ('out', 'Out Employment'), ],
                                  required=False, )

    journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    account_move_id = fields.Many2one(comodel_name="account.move", string="", )

    def create_account_move(self):
        move_line_1 = {
            'name': 'Order Labors',
            'account_id': self.debit_account_id.id,
            'debit': self.total_cost,
            'credit': 0.0,
            'partner_id': self.project_id.partner_id.id or False,
            'analytic_distribution': {self.project_id.analytic_account_id.id: 100} if self.project_id.analytic_account_id else False,
        }
        move_line_2 = {
            'name': 'Order Labors',
            'account_id': self.credit_account_id.id,
            'debit': 0.0,
            'credit': self.total_cost,
        }
        move_vals = {
            'name': 'Order Labors',
            'date': fields.Date.today() or False,
            'state': 'draft',
            'ref': 'Order Labors for %s' % self.project_id.name,
            'journal_id': self.journal_id.id,
            'labor_id': self.id,
            'line_ids': [(0, 0, move_line_2), (0, 0, move_line_1)],
        }
        account_move = self.env['account.move'].create(move_vals)
        self.account_move_id = account_move

    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('construction.labor.madina')) or 'New'
        return super(construction_labor, self).create(vals)


class construction_labor_line(models.Model):
    _name = 'construction.labor.line'

    _description = 'construction_service_labor_line'

    
    @api.depends('unit_cost', 'qty')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.qty * rec.unit_cost if rec.unit_cost and rec.qty else 0
        return True

    @api.onchange('labor_id')
    def onchange_labor_id(self):

        if self.labor_id:
            self.name = self.labor_id.name
            self.unit_cost = self.labor_id.unit_cost

    @api.onchange('order_qty')
    def onchange_order_qty(self):
        if self.order_qty:
            self.qty = self.order_qty

    labor_id = fields.Many2one(comodel_name="construction.labors", string="Labor", required=True, )
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='labor_id.product_uom_id', store=True,
                                     readonly=True)

    name = fields.Char(string="Titel", required=False, )
    order_labor_id = fields.Many2one(comodel_name="construction.labor", string="Order Labor", required=False, )
    unit_cost = fields.Float(string="Unit Cost", required=True, )
    order_qty = fields.Float(string="Qty", default=1, required=True, )
    qty = fields.Float(string="Approved Qty", default=1, required=True, )
    cost = fields.Float(string="Cost", compute="_compute_cost", store=True, required=False, )


class construction_labors(models.Model):
    _name = 'construction.labors'

    name = fields.Char(string="Name", required=True, )
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', )

    unit_cost = fields.Float(string="Cost", required=False, )
    unit_price = fields.Float(string="Price", required=False, )
    note = fields.Text(string="Note", required=False, )
