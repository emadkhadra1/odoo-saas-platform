# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ProgressBill(models.Model):
    _name = 'b2b.progress.bill'
    _inherit = ['mail.thread']
    _description = "Construction Quotation"

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
                    'consructor_id': [('is_constructors', '=', True)],
                }
            }

    name = fields.Integer(string="Quotation No.", readonly=True)
    purchase_order_id = fields.Many2one("b2b.construction.boq", string="Contractor Quotation", required=False, ondelete='cascade',)
    construction_type_id = fields.Many2one("b2b.constrution.type", string='Construction Type', readonly=False,
                                           required=True)
    project_id = fields.Many2one("construction.project", string='Project Name', required=True)
    consructor_id = fields.Many2one("res.partner", string='Contractor', required=True,
                                    domain="[('is_constructors', '=', True)]", store=True)
    progress_bill_type_id = fields.Many2one('b2b.progress.bill.type', string='Quotation Type', required=True)
    from_date = fields.Date(string='From', required=True, default=fields.Date.context_today, tracking=True)
    to_date = fields.Date(string='To', required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(STATUS, string="State", default="draft", required=True, tracking=True)
    line_ids = fields.One2many('b2b.progress.bill.lines', 'progress_bill_id', string='Construction Quotation Lines',
                               required=False)
    line2_ids = fields.One2many('b2b.progress.bill.lines2', 'progress_bill_id', string='Construction Quotation Lines',
                                required=False)
    deduction_ids = fields.Many2many('b2b.deductions', 'bill_deduction_rel', 'bill_id', 'deduction_id',
                                     string='Deductions')
    my_domain = fields.Many2many(comodel_name='b2b.deductions', string='Domain', relation='bill_deduction_rel1',
                                 column1='bill_id', column2='deduction_id', compute='_get_domain_str')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          related='project_id.analytic_account_id', store=True)
    work_amount_total = fields.Float(compute="_calculate_line_ids", string="Total", store=True,
                                     digits='Constructor price')
    already_cashed = fields.Float(string="Already Cashed", digits='Constructor price',compute='_calculate_already_cashed', store=True)
    down_payment = fields.Float(string="Down Payment", digits='Constructor price')
    down_payment_amount = fields.Float('قيمة الدفعة المقدمة', compute="compute_downpayment_amount")
    pay_required = fields.Float(compute="_calculate_pay_required", string="Pay Required",
                                digits='Constructor price')
    deductions = fields.Float(compute="_calculate_deduction", string="Deductions",
                              digits='Constructor price')
    pay_due = fields.Float(compute="_calculate_pay_due", string="Due for Pay", store=False,
                           digits='Constructor price')
    invoice_id = fields.Many2one("account.move", string="Account Invoice", readonly=True)
    invoice_remaining = fields.Float(compute="_get_residual", string="Invoice Remaining", readonly=True)
    journal_id = fields.Many2one("account.journal", string="Journal", required=True,
                                 domain="[('is_construction_journal', '=', True)]",
                                 context="{'default_is_construction_journal':True, }")
    quotation_type = fields.Selection(TYPING, string='Quotation Type', required=True)

    
    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        for rec in self:
            rec.consructor_id = None

    
    def _get_domain_str(self):
        for rec in self:

            doc = []

            for d in rec.consructor_id.deduction_ids:
                doc.append(d.deduction_id.id)
            rec.my_domain = doc
            # print('doc', doc)
            # return {'domain':[('deduction_ids','in',doc)]}
            # return {'domain': {'deduction_ids': [('id', 'in', doc)]}}

    
    @api.onchange('consructor_id')
    def _onchange_consructor_id(self):
        for rec in self:
            rec.line_ids = None
            rec.line2_ids = None
            notes = ''

            if rec.consructor_id and rec.quotation_type == "with_boq":
                lines = []
                constructor_items = self.env["b2b.entrepreneurs"].search([
                    ("purchase_order_id", "=", rec.purchase_order_id.id),
                    ("consructor_id", "=", rec.consructor_id.id),
                ])
                for line in constructor_items:
                    notes = ''
                    noteso = self.env["b2b.progress.bill.lines"].search([
                        ("main_item_id", "=", line.main_item_id.id),
                        ("sub_item_id", "=", line.sub_item_id.id),
                        ('purchase_order_id', '=', rec.purchase_order_id.id),
                        ('project_id', '=', rec.project_id.id),

                        ("business_statement_id", "=", line.business_statement_id.id),

                    ])
                    for e in noteso:
                        if e.notes:
                            notes += ' ' + e.notes
                    lines.append((0, 0, {
                        "progress_bill_id": rec.id,
                        "main_item_id": line.main_item_id.id,
                        "sub_item_id": line.sub_item_id.id,
                        "type_id": line.type_id.id,
                        "business_statement_id": line.business_statement_id.id,
                        "indexation_id": line.indexation_id.id,
                        "entrepreneurs_id": line.id,
                        'notes': notes,
                        'perc_c': 100,

                    }))
                rec.line_ids = lines
                doc = []

                for d in rec.consructor_id.deduction_ids:
                    doc.append(d.deduction_id.id)
                # return {'domain': {'deduction_ids': [('id','in',doc)]}}

    def open_invoices(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        account_ids = []
        boq = self.search([
            ("purchase_order_id", "=", self.purchase_order_id.id),
        ])

        for b in boq:
            if b.invoice_id:
                account_ids.append(b.invoice_id.id)

        result['domain'] = [('id', 'in', account_ids)]
        return result

    
    def action_send_by_mail(self):
        for rec in self:
            pass

    
    def action_print(self):
        data = {
            'ids': [self.id],
            'model': 'b2b.progress.bill',
            'form': self.id
        }
        return self.env.ref('b2b_constructors.report_b2b_qoutation_print').report_action(self)

        return self.env['report'].get_action(self, "b2b_constructors.b2b_qoutation_report")

    
    @api.depends('project_id', 'consructor_id', 'purchase_order_id')
    def _calculate_already_cashed(self):
        for rec in self:
            old_payment = 0.0
            old_payment_2 = 0.0
            domain = [("project_id", "=", rec.project_id.id),("consructor_id", "=", rec.consructor_id.id),("purchase_order_id", "=", rec.purchase_order_id.id), ('name', '<', rec.name)] if rec.quotation_type == "with_boq" else [("project_id", "=", rec.project_id.id),("consructor_id", "=", rec.consructor_id.id)]
            old_quotations = self.search(domain)

            # for s in old_quotations:
            #     print("pay_required - old_quotations >>>>>>>>>", s.pay_required)
            #     for p in s.invoice_id.payment_ids:
            #         old_payment += p.amount
            # print("old_payment", old_payment)
            # rec.already_cashed = old_payment

            for s in old_quotations:
                old_payment_2 += s.pay_required
            rec.already_cashed = old_payment_2

    @api.depends('down_payment')
    def compute_downpayment_amount(self):
        for rec in self:
            rec.down_payment_amount = rec.down_payment * (rec.work_amount_total - rec.already_cashed) / 100

    @api.onchange('project_id', 'consructor_id')
    def onchange_project(self):
        for rec in self:
            if rec.project_id.project_constructor_ids and rec.project_id.project_constructor_ids.filtered(lambda m: m.constructor_id.id == rec.consructor_id.id):
                rec.down_payment = rec.project_id.project_constructor_ids.filtered(lambda m: m.constructor_id.id == rec.consructor_id.id).downpayment

    @api.depends('work_amount_total', 'already_cashed', 'down_payment')
    def _calculate_pay_required(self):
        for rec in self:
            rec.pay_required = rec.work_amount_total - rec.already_cashed - (rec.down_payment * (rec.work_amount_total - rec.already_cashed) / 100)

    
    @api.depends('invoice_id')
    def _get_residual(self):
        for rec in self:
            rec.invoice_remaining = float(rec.invoice_id.amount_residual)

    
    @api.depends('pay_required', 'deductions')
    def _calculate_pay_due(self):
        for rec in self:
            rec.pay_due = rec.pay_required - rec.deductions

    
    @api.onchange('line2_ids','line_ids')
    @api.depends('line2_ids','line_ids')
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
                        total += (s.total_work * s.category) * (s.perc_c / 100)
            rec.work_amount_total = total
            # rec.notes = notes

    #
    # 
    # @api.depends('deduction_ids')
    # def _calculate_deduction(self):
    #     for rec in self:
    #         deduction = 0.0
    #         deduction = 0.0
    #         if rec.deduction_ids:
    #             for s in rec.deduction_ids:
    #                 deduction += s.amount
    #         rec.deductions = deduction
    
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
                        dic = {'name': d.name,
                               'type': d.type,
                               'amount': d.amount,
                               'account_id': d.account_id.id,
                               }
                        listemp.append((4, 0, dic))
                    each.deduction_ids = listemp

    
    def action_submit(self):
        for rec in self:
            if (rec.quotation_type == "with_boq" and not rec.line_ids) or (
                    rec.quotation_type == "without_boq" and not rec.line2_ids):
                raise ValidationError(_("يرجى إدخال البنود أولا."))
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
                for d in rec.line2_ids:
                    dic = {}
                    dic = {
                        'main_item_id': d.main_item_id.id,
                        'sub_item_id': d.sub_item_id.id,
                        # 'entrepreneurs_id': d.entrepreneurs_id.id,
                        'uom_id': d.uom_id.id,
                        'required_quantity': d.required_quantity,

                        'previous_work': d.previous_work,

                        'current_work': d.current_work,
                        'total_work': d.total_work,
                        'category': d.category,
                        'work_amount': d.work_amount,
                        'perc_c': d.perc_c,

                    }
                    quotation_ids.append((0, 0, dic))

                invoice_id = self.env["account.move"].sudo().create({
                    "name": "مستخلص بند اعمال",
                    "partner_id": rec.consructor_id.id,
                    "invoice_date": rec.from_date,
                    "invoice_date_due": rec.from_date,
                    "move_type": 'in_invoice',
                    "journal_id": rec.journal_id.id,
                    # 'owner_quotation_id': rec.id,
                    # "account_id": rec.journal_id.default_credit_account_id.id,

                    "invoice_line_ids": line,
                    "quotation_ids": quotation_ids
                })

                rec.write({
                    "state": "approve",
                    "invoice_id": invoice_id.id,
                })
            else:
                raise ValidationError(_("اليومية المحددة لا تحتوي على حساب دائن، يرجى إكماله أولا."))

    # 
    # def action_sent(self):
    #     for rec in self:
    #         if  rec.journal_id and  rec.journal_id.default_credit_account_id:
    #             invoice_id = self.env["account.invoice"].sudo().create({
    #                 "name": "مستخلص بند اعمال",
    #                 "partner_id": rec.consructor_id.id,
    #                 "date_invoice": rec.from_date,
    #                 "date_due": rec.from_date,
    #                 "type": 'in_invoice',
    #                 "journal_id": rec.journal_id.id,
    #                 "invoice_line_ids": [
    #                     (0, 0, {
    #                         'product_id': self.env.ref('b2b_constructors.b2b_boq_product0').id,
    #                         'quantity': 1.0,
    #                         'price_unit': rec.pay_due,
    #                         'name': 'مستخلص اعمال',
    #                         "account_id": rec.journal_id.default_credit_account_id.id,
    #                         }),
    #                 ],
    #             })
    #
    #             rec.write({
    #                 "state": "approve",
    #                 "invoice_id": invoice_id.id,
    #             })
    #         else:
    #             raise ValidationError(_("اليومية المحددة لا تحتوي على حساب دائن، يرجى إكماله أولا."))

    @api.model_create_multi
    def create(self, vals_list):
        records = self.browse()
        for vals in vals_list:
            if vals.get("quotation_type", False) == "with_boq":
                qoutation_no = self.search([
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

            records |= super(ProgressBill, self).create([vals])
        return records
