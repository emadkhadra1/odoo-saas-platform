from odoo.tools.translate import _
from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


class construction_transport(models.Model):
    _name = 'construction.transport'
    _rec_name = 'name'
    _description = 'construction_transport'
    _inherit = ['mail.thread', ]

    def unlink(self):
        if self.state == 'done':
            raise UserError(_('?? ????? ?????.'))
        return super(construction_transport, self).unlink()

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

    total_amount = fields.Float(string="إجمالي المبلغ", tracking=True, compute="_compute_total",
                                store=True,
                                required=False, )
    total_cost = fields.Float(string="إجمالي التكلفة", tracking=True, compute="_compute_total", store=True,
                              required=False, )
    name = fields.Char(string="المسلسل", tracking=True, required=False, )
    project_id = fields.Many2one(comodel_name="construction.project", tracking=True, string="المشروع",
                                 required=True, )
    date = fields.Date(string="التاريخ", default=_get_date_now, tracking=True, required=False, )
    state = fields.Selection(string="الحالة", default='new', tracking=True,
                             selection=[('new', 'New'), ('done', 'تم'), ],
                             required=False, )
    line_ids = fields.One2many(comodel_name="construction.transport.line", inverse_name="order_transport_id",
                               string="بنود النقل", required=False, )
    employment = fields.Selection(string="التوظيف", default='in', tracking=True,
                                  selection=[('in', 'Company Employment '), ('out', 'Out Employment'), ],
                                  required=False, )

    journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    account_move_id = fields.Many2one(comodel_name="account.move", string="", )
    boq_id = fields.Many2one(comodel_name="b2b.construction.boq", tracking=True, string="جدول الكميات",
                             required=True, domain="[('project_id', '=', project_id)]")
    business_item_ids = fields.Many2many(comodel_name="b2b.business.items", compute="compute_business_item_ids")
    business_item_id = fields.Many2one(comodel_name="b2b.business.items", tracking=True,
                                       string="بند أعمال", domain="[('id', 'in', business_item_ids)]")

    @api.depends('boq_id')
    def compute_business_item_ids(self):
        for rec in self:
            rec.business_item_ids = rec.boq_id.indexation_ids.mapped('business_statement_id').ids if rec.boq_id else False

    def create_account_move(self):
        move_line_1 = {
            'name': 'Order transports',
            'account_id': self.debit_account_id.id,
            'debit': self.total_cost,
            'credit': 0.0,
            'partner_id': self.project_id.partner_id.id or False,
            'analytic_distribution': {self.project_id.analytic_account_id.id: 100} if self.project_id.analytic_account_id else False,
        }
        move_line_2 = {
            'name': 'Order transports',
            'account_id': self.credit_account_id.id,
            'debit': 0.0,
            'credit': self.total_cost,
        }
        move_vals = {
            'name': 'Order transports',
            'date': fields.Date.today() or False,
            'state': 'draft',
            'ref': 'Order transports for %s' % self.project_id.name,
            'journal_id': self.journal_id.id,
            'transport_id': self.id,
            'line_ids': [(0, 0, move_line_2), (0, 0, move_line_1)],
        }
        account_move = self.env['account.move'].create(move_vals)
        self.account_move_id = account_move

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = (self.env['ir.sequence'].next_by_code('construction.transport.madina')) or 'New'
        return super(construction_transport, self).create(vals_list)


class construction_transport_line(models.Model):
    _name = 'construction.transport.line'

    _description = 'construction_service_transport_line'

    @api.depends('unit_cost', 'الكمية')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.qty * rec.unit_cost if rec.unit_cost and rec.qty else 0
        return True

    @api.onchange('transport_id')
    def onchange_transport_id(self):

        if self.transport_id:
            self.name = self.transport_id.name
            self.unit_cost = self.transport_id.unit_cost

    @api.onchange('order_qty')
    def onchange_order_qty(self):
        if self.order_qty:
            self.qty = self.order_qty

    transport_id = fields.Many2one(comodel_name="construction.transports", string="نقل", required=True, )
    product_uom_id = fields.Many2one('uom.uom', string='وحدة القياس', related='transport_id.product_uom_id', store=True,
                                     readonly=True)

    name = fields.Char(string="العنوان", required=False, )
    order_transport_id = fields.Many2one(comodel_name="construction.transport", string="طلب نقل", required=False, )
    unit_cost = fields.Float(string="تكلفة الوحدة", required=True, )
    order_qty = fields.Float(string="الكمية", default=1, required=True, )
    qty = fields.Float(string="الكمية المعتمدة", default=1, required=True, )
    cost = fields.Float(string="التكلفة", compute="_compute_cost", store=True, required=False, )
    transportation = fields.Float(string="النقل", compute="compute_labour_install")

    @api.depends('order_transport_id.business_item_id')
    def compute_labour_install(self):
        for rec in self:
            rec.transportation = sum(lab.transportation for lab in rec.order_transport_id.business_item_id.line_ids)


class construction_transports(models.Model):
    _name = 'construction.transports'

    name = fields.Char(string="الاسم", required=True, )
    product_uom_id = fields.Many2one('uom.uom', string='وحدة القياس', )
    unit_cost = fields.Float(string="التكلفة", required=False, )
    unit_price = fields.Float(string="السعر", required=False, )
    note = fields.Text(string="ملاحظة", required=False, )
