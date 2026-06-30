# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class QuotationReportWizard(models.TransientModel):
    _name = 'b2b.quotation.report.wizard'

    _description = "معالج تقرير عرض السعر"

    _rec_name = "project_id"

    project_id = fields.Many2one("construction.project", string='اسم المشروع', required=True)
    business_statement_id = fields.Many2one("b2b.business.items", string="بيان الأعمال", required=False)
    from_date = fields.Date(string='من', required=True,default=fields.Date.context_today)
    to_date = fields.Date(string='إلى', required=True,default=fields.Date.context_today)


    
    def action_print(self):
        active_ids = self.env.context.get('active_ids', [])
        # print('self.read()[0]',self.read()[0])
        datas = {
            'ids': active_ids,
            'model': 'b2b.quotation.report.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('b2b_constructors.b2b_report_sum_quotation').report_action([], data=datas)


# -*- coding: utf-8 -*-
# from __future__ import division
import time
import datetime
# from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pytz



class ReportMultilaserParser(models.AbstractModel):
    _name = 'report.b2b_constructors.report_b2b_qoutation_sum_document'

    
    def get_informations(self,d):
        param = self.sudo().env['b2b.quotation.report.wizard'].browse(d)
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
            # domain = []
            qoutation_lines = self.env["b2b.progress.bill.lines"].search(domain)
            qoutation_lines2 = self.env["b2b.progress.bill.lines2"].search(domain)

            if qoutation_lines or qoutation_lines2:
                data = {}
                bi_ids = []
                data["project"] = rec.project_id.name
                data["from_date"] = rec.from_date
                data["to_date"] = rec.to_date
                data["bi_ids"] = {}
                for line in qoutation_lines:
                    if line.business_statement_id and line.business_statement_id not in bi_ids:
                        bi_ids.append(line.business_statement_id)

                for line2 in qoutation_lines2:
                    if line2.business_statement_id and line2.business_statement_id not in bi_ids:
                        bi_ids.append(line2.business_statement_id)

                for bi in bi_ids:
                    data["bi_ids"][bi] = 0.0
                    for line in qoutation_lines:
                        if line.business_statement_id == bi:
                            data["bi_ids"][bi] += line.current_work

                    for line2 in qoutation_lines2:
                        if line2.business_statement_id == bi:
                            data["bi_ids"][bi] += line2.current_work
            else:
                raise ValidationError(_("?? ???? ??????!"))
            # for k, v in data["bi_ids"].items():
            #     print('v',v)
            #     print('k',k)
            #
            #     print('name',k.name)
            #     data["bi_ids"][k.name] = v
            #     del data["bi_ids"][k]

            new_bi = []
            for item in data['bi_ids'].items():
                new_bi.append(item)

            data["bi_ids"] = new_bi
            return [data]

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') and not docids:
            raise UserError(_("????? ??????? ??? ?????? ?? ???? ????? ???????."))
        if not docids:
            id = data.get('form')['id']

            docids=[id]
        register_ids = self.env.context.get('active_ids', [])

        return {
            'doc_ids': docids,
            'doc_model': 'b2b.progress.bill.lines',
            'docs': register_ids,
            'data': data,

            'get_informations':self.get_informations,

        }