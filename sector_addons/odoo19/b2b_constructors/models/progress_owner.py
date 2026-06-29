# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class invoice(models.Model):
    _inherit = 'account.move'
    owner_quotation_id = fields.Many2one('b2b.progress.owner')


class ProgressOwner(models.Model):
    _name = 'b2b.progress.owner'
    _inherit = ['mail.thread']
    _description = "Owner Quotation"

    _rec_name = "consructor_id"
    _order = 'id desc'

    STATUS = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("cancel", "Cancel"),

        ("approve", "Approve"),
    ]

    TYPING = [
        ("with_boq", "With BOQ"),
        ("without_boq", "Without BOQ"),
    ]

    @api.onchange('quotation_type')
    def onchange_quotation_type(self):
        self.purchase_order_id = None
        self.construction_type_id = None
        self.project_id = None
        self.consructor_id = None

    @api.onchange('purchase_order_id')
    def onchange_purchase_order_id(self):
        if self.purchase_order_id:
            self.construction_type_id = self.purchase_order_id.construction_type_id if self.purchase_order_id else None
            self.project_id = self.purchase_order_id.project_id if self.purchase_order_id else None

        if self.purchase_order_id and self.purchase_order_id.constructor_ids:
            constructor_ids = [
                x.consructor_id.id for x in self.purchase_order_id.constructor_ids]
            return {'domain':
                {
                    'consructor_id': [
                        ('id', 'in', constructor_ids),
                    ],
                }
            }
        else:
            return {'domain':
                {
                    'consructor_id': [],
                }
            }

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            self.consructor_id = self.project_id.partner_id if self.project_id else None
            self.analytic_account_id = self.project_id.analytic_account_id if self.project_id else None

            #     self.project_id = self.purchase_order_id.project_id if self.purchase_order_id else None
            #     constructor_ids = [
            #         x.consructor_id.id for x in self.purchase_order_id.constructor_ids]
            #     return {'domain':
            #             {
            #                 'consructor_id': [
            #                     ('id', 'in', constructor_ids),
            #                 ],
            #             }
            #             }
            # else:
            #     return {'domain':
            #             {
            #                 'consructor_id': [('is_constructors', '=', True)],
            #             }
            #             }

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          related='project_id.analytic_account_id', store=True)
    name = fields.Integer(string="Quotation No.", readonly=True, default=0)
    purchase_order_id = fields.Many2one("b2b.construction.boq", string="Contractor Quotation", required=False)
    construction_type_id = fields.Many2one("b2b.constrution.type", string='Construction Type', readonly=False,
                                           required=True)
    project_id = fields.Many2one("construction.project", string='Project Name', required=True)
    consructor_id = fields.Many2one("res.partner", string='Customer', required=True, store=True)
    progress_bill_type_id = fields.Many2one('b2b.progress.bill.type', string='Quotation Type', required=True)
    from_date = fields.Date(string='From', required=True, default=fields.Date.context_today, tracking=True)
    to_date = fields.Date(string='To', required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(STATUS, string="State", default="draft", required=True, tracking=True)
    line_ids = fields.One2many('b2b.progress.owner.lines', 'progress_bill_id', string='Construction Quotation Lines',
                               required=False, ondelete='cascade',)
    line2_ids = fields.One2many('b2b.progress.owner.lines2', 'progress_bill_id', string='Construction Quotation Lines',
                                required=False, ondelete='cascade',)
    deduction_ids = fields.Many2many('b2b.deductions', 'owner_deduction_rel', 'owner_id', 'deduction_id',
                                     string='Deductions')
    my_domain = fields.Many2many(comodel_name='b2b.deductions', string='Domain', relation='bill_deduction_rel1',
                                 column1='bill_id', column2='deduction_id', compute='_get_domain_str')

    work_amount_total = fields.Float(compute="_calculate_line_ids", string="Total",store=True,digits='Constructor price')
    already_cashed = fields.Float(compute="_calculate_already_cashed", string="Already Cashed",digits='Constructor price', store=True)
    down_payment = fields.Float(string="Down Payment",digits='Constructor price', related="project_id.owner_downpayment")
    down_payment_amount = fields.Float('DownPayment Amount', compute="compute_downpayment_amount")
    pay_required = fields.Float(compute="_calculate_pay_required", string="Pay Required",digits='Constructor price')
    deductions = fields.Float(compute="_calculate_deduction", string="Deductions",digits='Constructor price')
    pay_due = fields.Float(compute="_calculate_pay_due", string="Due for Pay",store=False,digits='Constructor price')
    invoice_id = fields.Many2one("account.move", string="Account Invoice", readonly=True)
    invoice_remaining = fields.Float(compute="_get_residual", string="Invoice Remaining", readonly=True)
    journal_id = fields.Many2one("account.journal", string="Journal", required=True,
                                 domain="[('type', '=', 'sale'),('is_construction_journal', '=', True)]",
                                 context="{'default_is_construction_journal':True, }")
    quotation_type = fields.Selection(TYPING, string='Quotation Type', required=True)
    business_statement_domain_ids = fields.Many2many(related="purchase_order_id.business_statement_domain_ids")
    business_item_ids = fields.Many2many(comodel_name="b2b.business.items", relation="owner_bill_business_items2_rel", column1="owner_bill_id", column2="business_item_id", string="Business Statements", )

    # 
    # def button_insert_lines(self):
    #     lines_values = self.purchase_order_id.indexation_ids.search([('business_statement_id', 'in', self.business_item_ids.ids), ('purchase_order_id', '=', self.purchase_order_id.id)])
    #     lines = []
    #     env_entrepreneur = self.env['b2b.entrepreneurs']
    #     for val in lines_values:
    #         entrepreneur_id = env_entrepreneur.search([('business_statement_id', '=', val.business_statement_id.id)], limit=1)
    #         lines.append((0, 0, {
    #             'main_item_id': val.main_item_id.id, 'sub_item_id': val.sub_item_id.id,
    #             'sub_business_statement_id': val.sub_business_statement_id.id, 'perc_c': 100,
    #             'business_statement_id': val.business_statement_id.id, 'uom_id': val.uom_id.id,
    #             'required_quantity': val.required_quantity, 'category': val.category, 'entrepreneurs_id': entrepreneur_id and entrepreneur_id.id or False
    #         }))
    #     if self.line_ids:
    #         self.line_ids = [(5, 0, 0)]
    #     self.line_ids = lines

    
    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        for rec in self:
            rec.consructor_id = None

    
    @api.onchange('consructor_id')
    def _onchange_consructor_id(self):
        indexation = self.env["b2b.indexation"]
        env_progress_owner_lines = self.env["b2b.progress.owner.lines"]
        for rec in self:
            rec.line_ids = None
            rec.line2_ids = None
            notes = ''

            if rec.consructor_id and rec.quotation_type == "with_boq":
                lines = []
                constructor_items = indexation.search([
                    ("purchase_order_id", "=", rec.purchase_order_id.id),
                    # ("consructor_id", "=", rec.consructor_id.id),
                ])
                for line in constructor_items:
                    notes = ''
                    noteso = env_progress_owner_lines.search([
                        ("main_item_id", "=", line.main_item_id.id),
                        ("sub_item_id", "=", line.sub_item_id.id),
                        ('purchase_order_id', '=', rec.purchase_order_id.id),
                        ('project_id', '=', rec.project_id.id),
                        ("business_statement_id", "=", line.business_statement_id.id),

                    ])
                    for e in noteso:
                        if e.notes:
                            notes += ' ' + e.notes
                    entrepreneurs_id = self.env['b2b.entrepreneurs'].search([('indexation_id', '=', line.id)], limit=1)

                    lines.append((0, 0, {
                        "progress_bill_id": rec.id,
                        "main_item_id": line.main_item_id.id,
                        "sub_item_id": line.sub_item_id.id,
                        "business_statement_id": line.business_statement_id.id,
                        "sub_business_statement_id": line.sub_business_statement_id.id,
                        "indexation_id": line.id,
                        "entrepreneurs_id": entrepreneurs_id and entrepreneurs_id.id or False,
                        'category': line.category,
                        'uom_id': line.uom_id.id,
                        'current_work': line.finished_quantity,
                        'notes': notes,
                        'perc_c': 100,
                        'required_quantity': line.required_quantity,
                    }))
                rec.line_ids = lines
                doc = []

                for d in rec.consructor_id.deduction_ids:
                    doc.append(d.deduction_id.id)
        return
        for rec in self:
            doc = []

            for d in rec.consructor_id.deduction_ids:
                doc.append(d.deduction_id.id)
            # return {'domain':[('deduction_ids','in',doc)]}
            return {'domain': {'deduction_ids': [('id', 'in', doc)]}}

    def open_invoices(self):
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        account_ids = []
        boq = self.env['account.move'].search([
            ("owner_quotation_id", "=", self.id),
        ])

        for b in boq:
            if b:
                account_ids.append(b.id)

        result['domain'] = [('id', 'in', account_ids)]
        return result

    
    def action_send_by_mail(self):
        for rec in self:
            pass

    
    def action_print(self):
        data = {
            'ids': [self.id],
            'model': 'b2b.progress.owner',
            'form': self.id
        }
        return self.env.ref('b2b_constructors.report_b2b_owner_qoutation_print').report_action(self)

        return self.env['report'].get_action(self, "b2b_constructors.b2b_qoutation_report")

    
    @api.depends('project_id', 'consructor_id', )
    def _calculate_already_cashed(self):
        for rec in self:
            old_payment = 0.0
            domain = [("project_id", "=", rec.project_id.id),("consructor_id", "=", rec.consructor_id.id),("purchase_order_id", "=", rec.purchase_order_id.id)] if rec.quotation_type == "with_boq" else [("project_id", "=", rec.project_id.id),("consructor_id", "=", rec.consructor_id.id)]
            old_quotations = self.search(domain)

            for s in old_quotations:
                # for p in s.invoice_id.payment_ids:
                if s.invoice_id.state not in ['draft', 'cancel']:
                    old_payment += s.invoice_id.amount_total

            rec.already_cashed = old_payment

    @api.depends('work_amount_total', 'already_cashed', 'down_payment')
    def _calculate_pay_required(self):
        for rec in self:
            rec.pay_required = rec.work_amount_total - rec.already_cashed - (rec.down_payment * (rec.work_amount_total - rec.already_cashed) / 100)

    @api.depends('down_payment')
    def compute_downpayment_amount(self):
        for rec in self:
            rec.down_payment_amount = rec.down_payment * (rec.work_amount_total - rec.already_cashed) / 100

    @api.depends('invoice_id')
    def _get_residual(self):
        for rec in self:
            rec.invoice_remaining = float(rec.invoice_id.amount_residual)

    @api.depends('pay_required', 'deductions')
    def _calculate_pay_due(self):
        for rec in self:
            rec.pay_due = rec.pay_required - rec.deductions

    # 
    # @api.onchange('line_ids')
    # @api.depends('line_ids')
    # def _calculate_line_ids(self):
    #     for rec in self:
    #         total = 0.0
    #         # if 1:  # rec.quotation_type == "with_boq":
    #         #     if rec.line_ids:
    #         #         for s in rec.line_ids:
    #         #             total += s.total_work * s.category
    #         # else:
    #         #     if rec.line2_ids:
    #         #         for s in rec.line2_ids:
    #         #             total += s.total_work * s.category
    #         # rec.work_amount_total = total
    #
    #         if 1: #rec.quotation_type == "with_boq":
    #             if rec.line_ids:
    #                 for s in rec.line_ids:
    #                     total += (s.total_work * s.category) * (s.perc_c / 100)
    #                     if s.notes:
    #                         notes += s.notes + ' '
    #         else:
    #             if rec.line2_ids:
    #                 for s in rec.line2_ids:
    #                     total += (s.total_work * s.category) * (s.perc_c / 100)
    #         rec.work_amount_total = total
    
    @api.onchange('line2_ids', 'line_ids')
    @api.depends('line2_ids', 'line_ids')
    def _calculate_line_ids(self):
        for rec in self:
            total = 0.0
            notes = ''

            if rec.quotation_type == "with_boq":
                if rec.line_ids:
                    for s in rec.line_ids:
                        total += (s.total_work * s.category) * (s.perc_c / 100)
                        if s.notes:
                            notes += s.notes + ' '
            else:
                if rec.line2_ids:
                    for s in rec.line2_ids:
                        total += (s.total_work * s.category) #* (s.perc_c / 100)
            rec.work_amount_total = total
            # rec.notes = notes

    def _get_domain_str(self):
        for rec in self:

            doc = []

            for d in rec.consructor_id.deduction_ids:
                doc.append(d.deduction_id.id)
            rec.my_domain = doc
            # print('doc', doc)
            # return {'domain':[('deduction_ids','in',doc)]}
            # return {'domain': {'deduction_ids': [('id', 'in', doc)]}}
    
    @api.depends('deduction_ids')
    def _calculate_deduction(self):
        for rec in self:
            deduction = 0.0
            if rec.deduction_ids:
                for s in rec.deduction_ids:
                    if s.type == 'amount':
                        deduction += s.amount
                    if s.type == 'percent':
                        deduction += rec.work_amount_total * (s.amount / 100)
            rec.deductions = deduction

    def check_deduction(self):
        self.deduction_ids.unlink()

        for each in self:
            if each.consructor_id:
                if each.consructor_id.deduction_ids:
                    listemp = []
                    for d in each.consructor_id.deduction_ids:
                        # dic = {'name': d.name,
                        #        'type': d.type,
                        #        'amount': d.amount,
                        #        'account_id':d.account_id.id,
                        #        }
                        dic = {'id': d.deduction_id.id,
                               # 'type': d.type,
                               # 'amount': d.amount,
                               # 'account_id': d.account_id.id,
                               }
                        listemp.append((0, 0, dic))
                    each.write({'deduction_ids': listemp})

    def action_submit(self):
        for rec in self:
            if (rec.quotation_type == "with_boq" and not rec.line_ids) or (
                    rec.quotation_type == "without_boq" and not rec.line2_ids):
                # if not rec.line_ids:

                raise ValidationError(_("Please, Enter Lines first!"))
            else:
                rec.write({
                    "state": "sent",
                })

    def action_cancel(self):
        for rec in self:
            rec.write({
                "state": "cancel",
            })
    
    def action_reset(self):
        for rec in self:
            rec.write({
                "state": "draft",
            })

    def action_sent(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.default_account_id:
                line = []
                dic = {}
                dic = {
                    'product_id': self.env.ref('b2b_constructors.b2b_boq_product0').id,
                    'quantity': 1.0,
                    'price_unit': rec.pay_required,
                    'name': 'مستخلص اعمال',
                    "account_id": rec.journal_id.default_account_id.id,
                    "analytic_distribution": {rec.analytic_account_id.id: 100} if rec.analytic_account_id else False,
                }
                line.append((0, 0, dic))

                for d in rec.deduction_ids:
                    deduction = 0
                    if d.type == 'amount':
                        deduction = d.amount
                    if d.type == 'percent':
                        deduction = rec.work_amount_total * (d.amount / 100)
                    dic = {}
                    dic = {
                        'quantity': 1.0,
                        'price_unit': -deduction,
                        'name': d.name,
                        "account_id": d.account_id.id,
                        # "account_analytic_id": rec.analytic_account_id and rec.analytic_account_id.id or False,
                    }
                    line.append((0, 0, dic))

                quotation_ids = []
                dic = {}
                for d in rec.line_ids:
                    dic = {}
                    dic = {
                        'main_item_id': d.main_item_id.id,
                        'sub_item_id': d.sub_item_id.id,
                        'entrepreneurs_id': d.entrepreneurs_id.id,
                        'uom_id': d.uom_id.id,
                        'required_quantity': d.required_quantity,

                        'previous_work': d.previous_work,

                        'current_work': d.current_work,
                        'total_work': d.total_work,
                        'category': d.category,
                        'work_amount': d.work_amount,
                        'perc_c': d.perc_c,
                        'notes': d.notes,

                    }
                    quotation_ids.append((0, 0, dic))
                invoice_id = self.env["account.move"].sudo().create({
                    "name": "مستخلص بند اعمال للماك",
                    "partner_id": rec.consructor_id.id,
                    "invoice_date": rec.from_date,
                    "invoice_date_due": rec.from_date,
                    "move_type": 'out_invoice',
                    "journal_id": rec.journal_id.id,
                    'owner_quotation_id': rec.id,
                    # "account_id": rec.journal_id.default_credit_account_id.id,
                    "quotation_ids": quotation_ids,
                    "invoice_line_ids": line,
                })

                rec.write({
                    "state": "approve",
                    "invoice_id": invoice_id.id,
                })
            else:
                raise ValidationError(_("Selected Journal has not Credit Account!, Please, fill it first!"))

    @api.model_create_multi
    def create(self, vals_list):
        records = self.browse()
        for vals in vals_list:
            if vals.get("quotation_type", False) == "with_boq":
                qoutation_no = self.search([
                    ("project_id", "=", vals.get("project_id")),
                    ("consructor_id", "=", vals.get("consructor_id")),
                    ("purchase_order_id", "=", vals.get("purchase_order_id")),
                ], order="name desc", limit=1)
                vals["name"] = (qoutation_no.name + 1) if qoutation_no else 1
            else:
                qoutation_no = self.search([
                    ("consructor_id", "=", vals.get("consructor_id")),
                    ("project_id", "=", vals.get("project_id")),
                    ("construction_type_id", "=", vals.get("construction_type_id")),
                ], order="name desc", limit=1)
                vals["name"] = (qoutation_no.name + 1) if qoutation_no else 1

            records |= super(ProgressOwner, self).create([vals])
        return records
