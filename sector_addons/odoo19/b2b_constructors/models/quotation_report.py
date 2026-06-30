# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api, tools


class QuotationReport(models.Model):
    _name = 'b2b.quotation.report'

    _description = "تقرير عرض السعر"

    _auto = False

    _order = 'project_id desc'

    _rec_name = "project_id"

    project_id = fields.Many2one("construction.project", string='اسم المشروع', readonly=True)
    business_statement_id = fields.Many2one("b2b.business.items", string="بيان الأعمال", readonly=True)
    quantity = fields.Float(string="الكمية", readonly=True)
    from_date = fields.Date(string='من', readonly=True)
    to_date = fields.Date(string='إلى', readonly=True)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'b2b_quotation_report')
        self._cr.execute("""CREATE OR REPLACE VIEW  b2b_quotation_report AS (
                        SELECT
                            MIN(b2b_progress_bill_lines.id) AS id,
                            b2b_progress_bill.project_id as project_id,
                            b2b_progress_bill_lines.business_statement_id as business_statement_id,
                            SUM(b2b_progress_bill_lines.current_work) as quantity
                        FROM
                            public.b2b_progress_bill LEFT JOIN public.b2b_progress_bill_lines ON b2b_progress_bill.id = b2b_progress_bill_lines.progress_bill_id
                        GROUP BY
                            b2b_progress_bill.project_id, b2b_progress_bill_lines.business_statement_id )
                            """)
