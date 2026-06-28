# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError
from odoo.fields import Date, Datetime
from datetime import date, datetime, time, timedelta
import time
from odoo import api, models, _
from odoo.exceptions import UserError


class InsuranceWizardReport(models.TransientModel):
    _name = "insurance.wizard.report"

    month = fields.Selection([('1', 'January'),
                              ('2', 'February'),
                              ('3', 'March'),
                              ('4', 'April'),
                              ('5', 'May'),
                              ('6', 'June'),
                              ('7', 'July'),
                              ('8', 'August'),
                              ('9', 'September'),
                              ('10', 'October'),
                              ('11', 'November'),
                              ('12', 'December')
                              ], string="Month")
    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employee/s",
                                    domain=lambda x: [('company_id', '=', x.env.user.company_id.id)])
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company, required=True)

    def print_report(self):
        data = {}
        data['form'] = {}
        data['form'].update({'report_id': self.id})
        return self.env.ref('social_insurance.print_insurance_report_id').report_action(self, data=data)

    def get_month_label(self):
        month = date.today().replace(month=int(self.month)).strftime('%B')
        return month


class ReportInsurance(models.AbstractModel):
    _name = 'report.social_insurance.print_report_template'

    def get_data(self, report):
        start_date = date.today().replace(month=int(report.month), day=1)
        domain = [('state', '=', 'done'), ('company_id', '=', report.company_id.id), ('date_from', '<=', start_date),
                  ('date_to', '>=', start_date), ('is_insured', '=', True)]
        if report.employee_ids:
            domain.append(('employee_id', 'in', report.employee_ids.ids))

            # contracts = report.employee_ids.mapped('contract_ids').filtered(lambda x:x.is_insured and x.state=='open')
        # else:
        #     contracts = self.env['hr.contract'].search(
        #         [('company_id', '=', self.env.user.company_id.id), ('is_insured', '=', True), ('state', '=', 'open'),
        #          ('date_start', '>=', start_date)])
        payslips = self.env['hr.payslip'].search(domain)

        if not payslips:
            raise exceptions.ValidationError(
                'There is no data to print,perhaps there is no employee has insured or there is no payslips in this month!!')
        return payslips

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        #
        model = self.env['insurance.wizard.report']
        report = model.browse(data['form'].get('report_id'))
        res = self.get_data(report)

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': model.browse(docids),
            'data': res,
            'doc': report,
            'type': 'qweb-pdf',
        }
