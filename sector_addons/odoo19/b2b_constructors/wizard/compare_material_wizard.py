# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, ().
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class comparematerialReportWizard(models.TransientModel):
    _name = 'b2b.compare.material.report.wizard'

    _description = "compare material Report Wizard"

    _rec_name = "project_id"

    project_id = fields.Many2one("construction.project", string='Project Name', required=True)
    business_statement_ids = fields.Many2many("b2b.business.items", string="Business Statement", required=False)
    from_date = fields.Date(string='From', required=True, default=fields.Date.context_today)
    to_date = fields.Date(string='To', required=True, default=fields.Date.context_today)

    # main_item_id = fields.Many2one("b2b.main.items", string="Main Item", required=False)
    # sub_item_id = fields.Many2one("b2b.sub.items", string="Sub Item", required=False)
    # type = fields.Selection(string="Type",selection=[('material', 'Material'), ('working', 'Working'), ('both', 'Both')],default='both', )



    
    def action_print(self):
        active_ids = self.env.context.get('active_ids', [])
        # print('self.read()[0]',self.read()[0])
        datas = {
            'ids': active_ids,
            'model': 'b2b.compare.material.report.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('b2b_constructors.b2b_report_sum_compare_material').report_action([], data=datas)


# -*- coding: utf-8 -*-
# from __future__ import division
import time
import datetime
# from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pytz


class ReportMultilcomparematerialParser(models.AbstractModel):
    _name = 'report.b2b_constructors.report_b2b_c_material_sum_document'

    def get_boq(self, d, business_statement_id):
        param = self.sudo().env['b2b.compare.material.report.wizard'].browse(d)

        for rec in param:
            domain = [
                ("purchase_order_id.project_id", "=", rec.project_id.id),
                ("purchase_order_id.date_order", ">=", rec.from_date),
                ("purchase_order_id.date_order", "<=", rec.to_date),
                ("business_statement_id", "=", business_statement_id.id),

            ]

            domain.append(
                ("purchase_order_id.state", "=", 'assigned'),
            )
            # domain = []
            boq_lines = self.env["b2b.indexation"].search(domain)

            qty = 0
            if boq_lines:
                for line in boq_lines:
                    qty = qty + line.required_quantity

            return qty

    def get_construction(self, d, business_statement_id):
        param = self.sudo().env['b2b.compare.material.report.wizard'].browse(d)

        for rec in param:
            domain = [
                ("project_id", "=", rec.project_id.id),
                ("progress_bill_id.from_date", ">=", rec.from_date),
                ("progress_bill_id.to_date", "<=", rec.to_date),
                ("business_statement_id", "=", business_statement_id.id),

            ]

            domain.append(
                ("progress_bill_id.state", "=", 'approve'),
            )
            # domain = []
            boq_lines = self.env["b2b.progress.bill.lines"].search(domain)
            qoutation_lines2 = self.env["b2b.progress.bill.lines2"].search(domain)

            qty = 0
            if boq_lines:
                for line in boq_lines:
                    qty = qty + line.current_work
            if qoutation_lines2:
                for line in qoutation_lines2:
                    qty = qty + line.current_work
            return qty

    def get_owner(self, d, business_statement_id):
        param = self.sudo().env['b2b.compare.material.report.wizard'].browse(d)

        for rec in param:
            domain = [
                ("project_id", "=", rec.project_id.id),
                ("progress_bill_id.from_date", ">=", rec.from_date),
                ("progress_bill_id.to_date", "<=", rec.to_date),
                ("entrepreneurs_id.business_statement_id", "=", business_statement_id.id),

            ]

            domain.append(
                ("progress_bill_id.state", "=", 'approve'),
            )
            domain2 = [
                ("project_id", "=", rec.project_id.id),
                ("progress_bill_id.from_date", ">=", rec.from_date),
                ("progress_bill_id.to_date", "<=", rec.to_date),
                ("business_statement_id", "=", business_statement_id.id),

            ]

            domain2.append(
                ("progress_bill_id.state", "=", 'approve'),
            )
            # domain = []
            boq_lines = self.env["b2b.progress.owner.lines"].search(domain)
            qoutation_lines2 = self.env["b2b.progress.owner.lines2"].search(domain2)
            qty = 0
            if boq_lines:
                for line in boq_lines:
                    qty = qty + line.current_work
            if qoutation_lines2:
                for line in qoutation_lines2:
                    qty = qty + line.current_work
            return qty

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') and not docids:
            raise UserError(_("Form content is missing, this report cannot be printed."))
        if not docids:
            id = data.get('form')['id']

            docids = [id]
        register_ids = self.env.context.get('active_ids', [])
        param = self.sudo().env['b2b.compare.material.report.wizard'].browse(docids)
        project_id = ''
        from_date = False
        to_date = False
        business_statement_ids = []
        for rec in param:
            project_id = rec.project_id.name
            from_date = rec.from_date
            to_date = rec.to_date
            for e in rec.business_statement_ids:
                business_statement_ids.append(e)
        return {
            'doc_ids': docids,
            'doc_model': 'b2b.progress.bill.lines',
            'docs': register_ids,
            'data': data,
            'project': project_id,
            'from_date': from_date,
            'to_date': to_date,
            'business_statement_ids': business_statement_ids,
            'get_boq': self.get_boq,
            'get_construction': self.get_construction,
            'get_owner': self.get_owner,
        }
