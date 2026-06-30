from odoo import api, fields, models


class FinancialCustodyReportWizard(models.TransientModel):
    _name = 'financial.custody.report.wizard'
    _rec_name = 'name'
    _description = 'Financial Custody Report Wizard'
    
    name = fields.Char(string="Name", required=False, )
    day_from = fields.Date(string="Start Date", required=False, default=fields.Date.context_today)
    day_to = fields.Date(string="End Date", required=False, default=fields.Date.context_today)

    def print_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        # self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        # res = self.read()
        # res = res and res[0] or {}
        # data.update({'form': res})
        records = self.env['financial.custody'].search_read(domain=[('create_date', '>=', self.day_from), ('create_date', '<=', self.day_to)], fields=['due_date', 'name', 'custody_amount', 'partner_id', 'analytic_account_id', 'create_date', 'create_uid'])
        total_amount = sum([rec['custody_amount'] for rec in records])
        data.update({'custody_records': records, 'total_amount': total_amount})
        return self.env.ref('financial_custody.financial_custody_report').report_action(self, data=data)


    