# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta

class EmployeeDocuments(models.Model):
    _inherit = 'res.documents'

    def open_expiry_documents(self):
        context = self.env.context.copy()
        context['group_by'] = ['employee_id']
        expiry_docs = []
        expire_date = (fields.Date.context_today(self)+relativedelta(months=self.env.company.expiry_duration)).strftime('%Y-%m-%d')
        docs = self.env['res.documents'].search([('expiry_date', '<=', expire_date)])
        for doc in docs:
            expiry_docs.append(doc.id)

        views = [
            (self.env.ref('documents_expiry_report.employee_document_report_tree_view').id, 'tree'),
        ]

        if expiry_docs:
            domain = expiry_docs
            return {
                'type': 'ir.actions.act_window',
                'name': _('Employees Documents'),
                'res_model': 'res.documents',
                'view_id': self.env.ref('documents_expiry_report.employee_document_report_tree_view').id,
                'view_mode': 'tree',
                'views': views,
                'domain': [('id', 'in', domain)],
                'context': context
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Employees Documents'),
                'res_model': 'res.documents',
                'view_id': self.env.ref('documents_expiry_report.employee_document_report_tree_view').id,
                'view_mode': 'tree',
                'views': views,
                'domain': [('id', '=', -1)],
                'context': context
            }