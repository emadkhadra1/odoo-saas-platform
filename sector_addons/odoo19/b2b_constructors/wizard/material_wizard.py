# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class materialReportWizard(models.TransientModel):
    _name = 'b2b.material.report.wizard'

    _description = "material Report Wizard"

    _rec_name = "project_id"

    project_id = fields.Many2one("construction.project", string='Project Name', required=True)
    business_statement_id = fields.Many2one("b2b.business.items", string="Business Statement", required=False)
    from_date = fields.Date(string='From', required=True,default=fields.Date.context_today)
    to_date = fields.Date(string='To', required=True,default=fields.Date.context_today)
    main_item_id = fields.Many2one("b2b.main.items", string="البند الرئيسي", required=False)
    sub_item_id = fields.Many2one("b2b.sub.items", string="البند الفرعي", required=False)
    type = fields.Selection(string="Type",selection=[('material', 'Material'), ('working', 'Working'), ('both', 'Both')],default='both', )



    
    def action_print(self):
        active_ids = self.env.context.get('active_ids', [])
        # print('self.read()[0]',self.read()[0])
        datas = {
            'ids': active_ids,
            'model': 'b2b.material.report.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('b2b_constructors.b2b_report_sum_material').report_action([], data=datas)


# -*- coding: utf-8 -*-
# from __future__ import division
# import time
# import datetime
# from datetime import datetime
# from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
# import pytz



class ReportMultilmaterialParser(models.AbstractModel):
    _name = 'report.b2b_constructors.report_b2b_material_sum_document'

    
    def get_material(self,d):
        param = self.sudo().env['b2b.material.report.wizard'].browse(d)


        for rec in param:
            domain = [
                ("project_id", "=", rec.project_id.id),
                ("date", ">=", rec.from_date),
                ("date", "<=", rec.to_date),
            ]


            if rec.main_item_id:
                domain.append(
                    ("main_item_id", "=", rec.main_item_id.id),
                )
            if rec.sub_item_id:
                domain.append(
                    ("sub_item_id", "=", rec.sub_item_id.id),
                )
            domain.append(
                ("state", "=", 'done'),
            )
            # domain = []
            qoutation_lines = self.env["stock.move"].search(domain)
            # qoutation_lines2 = self.env["b2b.progress.bill.lines2"].search(domain)
            data = {}
            bi_ids = []
            data["project"] = rec.project_id.name
            data["from_date"] = rec.from_date
            data["to_date"] = rec.to_date
            data["bi_ids"] = []
            if qoutation_lines :
                for line in qoutation_lines:
                    d = {}
                    d['product']=line.product_id.name
                    d['uom']=line.product_id.uom_id.name

                    d['qty']=line.product_uom_qty
                    d['category']=0
                    d['amount']=0
                    for e in  self.env["account.move"].search(([('stock_move_id','=',line.id)])):
                        d['amount'] = e.amount
                    d['category']=d['amount'] / d['qty']

                    bi_ids.append(d)

                    # if 1: # line.business_statement_id and line.business_statement_id not in bi_ids:
                    #     bi_ids.append(line)

                data["bi_ids"] = bi_ids

                        # for bi in bi_ids:
                #     data["bi_ids"][bi] = 0.0
                #     for line in qoutation_lines:
                #         if line.business_statement_id == bi:
                #             data["bi_ids"][bi] += line.current_work
                #
                #     for line2 in qoutation_lines2:
                #         if line2.business_statement_id == bi:
                #             data["bi_ids"][bi] += line2.current_work
            # else:
            #     raise ValidationError(_("لا توجد بيانات!"))


            # new_bi = []
            # for item in data['bi_ids'].items():
            #     new_bi.append(item)
            #
            # data["bi_ids"] = new_bi
            return [data]
    
    def get_informations(self,d):
        param = self.sudo().env['b2b.material.report.wizard'].browse(d)

        for rec in param:
            domain = [
                ("project_id", "=", rec.project_id.id),
                ("progress_bill_id.from_date", ">=", rec.from_date),
                ("progress_bill_id.to_date", "<=", rec.to_date),
            ]

            if rec.business_statement_id:
                domain.append(
                    ("business_statement_id", "=", rec.business_statement_id.id),
                )
            if rec.main_item_id:
                domain.append(
                    ("main_item_id", "=", rec.main_item_id.id),
                )
            if rec.sub_item_id:
                domain.append(
                    ("sub_item_id", "=", rec.sub_item_id.id),
                )
            # domain = []
            qoutation_lines = self.env["b2b.progress.bill.lines"].search(domain)
            qoutation_lines2 = self.env["b2b.progress.bill.lines2"].search(domain)
            data = {}
            bi_ids = []
            data["project"] = rec.project_id.name
            data["from_date"] = rec.from_date
            data["to_date"] = rec.to_date
            data["bi_ids"] = {}
            if qoutation_lines or qoutation_lines2:

                for line in qoutation_lines:
                    if 1: # line.business_statement_id and line.business_statement_id not in bi_ids:
                        bi_ids.append(line)

                for line2 in qoutation_lines2:
                    if 1: # line2.business_statement_id and line2.business_statement_id not in bi_ids:
                        bi_ids.append(line2)
                data["bi_ids"] = bi_ids

                        # for bi in bi_ids:
                #     data["bi_ids"][bi] = 0.0
                #     for line in qoutation_lines:
                #         if line.business_statement_id == bi:
                #             data["bi_ids"][bi] += line.current_work
                #
                #     for line2 in qoutation_lines2:
                #         if line2.business_statement_id == bi:
                #             data["bi_ids"][bi] += line2.current_work
            # else:
            #     raise ValidationError(_("لا توجد بيانات!"))


            # new_bi = []
            # for item in data['bi_ids'].items():
            #     new_bi.append(item)
            #
            # data["bi_ids"] = new_bi
            return [data]

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') and not docids:
            raise UserError(_("محتوى النموذج غير مكتمل، لا يمكن طباعة التقرير."))
        if not docids:
            id = data.get('form')['id']

            docids=[id]
        register_ids = self.env.context.get('active_ids', [])
        param = self.sudo().env['b2b.material.report.wizard'].browse(docids)
        type='both'
        project_id=''
        from_date=False
        to_date=False
        for rec in param:
            type=rec.type
            project_id=rec.project_id.name
            from_date=rec.from_date
            to_date=rec.to_date
        return {
            'doc_ids': docids,
            'doc_model': 'b2b.progress.bill.lines',
            'docs': register_ids,
            'data': data,
            'type': type,
            'project':project_id,
            'from_date': from_date,
            'to_date': to_date,

            'get_material': self.get_material,
            'get_informations': self.get_informations,

        }