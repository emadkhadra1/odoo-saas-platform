# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResDocumentType(models.Model):
    _name = 'res.document.type'
    _description = 'Document Type'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    can_upload_from_portal = fields.Boolean(string="Can Upload From Portal ?", )
    # is_egyptian = fields.Boolean(string="Is this document for egyptian ?", )

    _sql_constraints = [
        ('code', 'unique(code)', 'Code must be unique per Document!'),
    ]


class ResDocuments(models.Model):
    _name = 'res.documents'
    _inherit = ['mail.thread']

    type_id = fields.Many2one('res.document.type', 'Type')
    issue_place = fields.Char('Place of Issue', size=128)
    issue_date = fields.Date('Date of Issue', track_visibility='onchange')
    expiry_date = fields.Date('Date of Expiry', track_visibility='onchange')
    notes = fields.Text('Notes')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
                                  default=lambda self: self.get_employee())
    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    is_hard_copy = fields.Boolean('Hard Copy')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('issue', 'Issued'),
        ('refuse', 'Refused'),
        ('renew', 'Renew'),
        ('expiry', 'Expiry')
    ], string='Status', readonly=False, copy=False, default='draft', track_visibility='onchange')
    attach_status = fields.Selection(string="Attach Status", selection=[('attached', 'Attached'),
                                                                        ('not_attached', 'Not Attached')],
                                     compute="compute_attach_status",store=True)

    @api.model
    def create(self, values):
        res = super(ResDocuments, self).create(values)
        partner = [self.env.user.partner_id.id]
        if res.manager_id.user_id:
            partner.append(res.manager_id.user_id.partner_id.id)
        if res.employee_id.user_id:
            partner.append(res.employee_id.user_id.partner_id.id)
        res.message_subscribe(partner_ids=partner)
        return res

    def write(self, values):
        partner = []
        if values.get('manager_id'):
            employee = self.env['hr.employee'].browse(values.get('manager_id'))
            if employee.user_id:
                partner.append(employee.user_id.partner_id.id)
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            if employee.user_id:
                partner.append(employee.user_id.partner_id.id)
        # channel_id=self.env.ref('saudi_hr.manager_channel').id
        self.message_subscribe(partner_ids=partner)
        return super(ResDocuments, self).write(values)

    @api.depends('employee_id', 'type_id')
    def name_get(self):
        """
            Return name of document with employee name, document type & document number.
        """
        result = []
        for doc in self:
            name = doc.employee_id.name + ' ' + doc.type_id.name
            result.append((doc.id, name))
        return result

    @api.model
    def run_scheduler(self):
        """
            cron job for automatically sent an email,
            sent notification, your document expired after 1 month.
        """
        today = datetime.now().date()
        for document in self.search([('state', '=', 'issue')]):
            if document.expiry_date and document.employee_id.user_id:
                notification_date = (document.expiry_date - relativedelta(months=+1))
                if today == notification_date:
                    try:
                        template_id = self.env.ref('res_documents.email_template_res_documents_notify')
                    except ValueError:
                        template_id = False
                    email_to = ''
                    user = document.employee_id.user_id
                    if user.email:
                        email_to = email_to and email_to + ',' + user.email or email_to + user.email
                    template_id.write({'email_to': email_to, 'reply_to': email_to, 'auto_delete': False})
                    template_id.send_mail(document.id, force_send=True)
            if document.expiry_date and document.expiry_date == today:
                document.state = 'expiry'
                try:
                    template_id = self.env.ref('res_documents.email_template_res_document_expire')
                except ValueError:
                    template_id = False
                if template_id:
                    template_id.send_mail(document.id, force_send=True, raise_exception=False, email_values=None)
        return True

    def action_send_mail(self):
        """
            send mail using mail template
        """
        try:
            template_id = self.env.ref('res_documents.email_template_res_document')
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True, raise_exception=False, email_values=None)
        return True

    def set_draft(self):
        """
            sent the status of generating Document record in draft state
        """
        self.state = 'draft'

    def _add_followers(self):
        """
            Add employee and manager in followers
        """
        partner_ids = []
        if self.employee_id.user_id:
            partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.manager_id.user_id:
            partner_ids.append(self.manager_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def document_submit(self):
        """
            sent the status of generating Document record in confirm state
        """
        self._add_followers()
        self.state = 'confirm'

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
            return: employee_ids
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).ids
        return employee_ids[0] if employee_ids else False

    def document_issue(self):
        """
            sent the status of generating Document record in issue state and get issue date
        """
        self.write({'manager_id': self.get_employee(),
                    'state': 'issue',
                    'issue_date': datetime.today()})
        self._add_followers()
        self.action_send_mail()

    def document_refuse(self):
        """
            sent the status of generating Document record in refuse state
        """
        self.state = 'refuse'

    def document_renew(self):
        """
            sent the status of generating Document record is renew
        """
        self.write({'state': 'renew',
                    'expiry_date': False,
                    'issue_date': False})

    @api.depends('attachment_ids')
    def compute_attach_status(self):
        for rec in self:
            if len(rec.attachment_ids) > 0:
                rec.attach_status = 'attached'
            else:
                rec.attach_status = 'not_attached'


class HrEmployee(models.AbstractModel):
    _inherit = 'hr.employee.base'

    document_ids = fields.One2many('res.documents', 'employee_id', 'Document')
    documents_count = fields.Integer(string='Documents', compute="_compute_documents")

    def _compute_documents(self):
        """
            count total document related employee
        """
        for employee in self:
            documents = self.env['res.documents'].search([('employee_id', '=', employee.id)])
            employee.documents_count = len(documents) if documents else 0

    def action_documents(self):
        """
            Show employee Documents
        """
        self.ensure_one()
        tree_view = self.env.ref('res_documents.res_documents_view_tree')
        form_view = self.env.ref('res_documents.res_documents_view_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Documents'),
            'res_model': 'res.documents',
            'view_type': 'form',
            'view_mode': 'from',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id
            }
        }

    def generate_document(self):
        for rec in self:
            if rec.document_ids and len(rec.document_ids) == len(self.env.company.egyptian_employee_document_ids):
                raise ValidationError("Employee has documents Already!")
            elif rec.document_ids and len(self.document_ids) != len(self.env.company.egyptian_employee_document_ids):
                docs = self.env.company.egyptian_employee_document_ids - rec.document_ids.mapped('type_id')
                for doc in docs:
                    self.env['res.documents'].create({'type_id': doc.id,
                                                      'employee_id': rec.id})
            else:
                for doc in self.env.company.egyptian_employee_document_ids:
                    self.env['res.documents'].create({'type_id':doc.id,
                                                     'employee_id':rec.id})