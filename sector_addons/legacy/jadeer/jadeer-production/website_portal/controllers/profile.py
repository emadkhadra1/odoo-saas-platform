# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR
import werkzeug
import base64
from datetime import datetime, timedelta
class PortalProfile(CustomerPortal):

    def prepare_attachment(self, attach):
        encoded = None
        filename = None
        if attach:
            filename = attach.filename
            attachment = attach
            attachment = attachment.read()
            encoded = base64.b64encode(attachment)
        return filename, encoded

    def attachment_format(self, res_id, attach):
        filename = None
        if attach:
            filename = attach.filename
            attachment = attach
            attachment = attachment.read()
            Attachments = request.env['ir.attachment'].sudo()
            attachment_id = Attachments.create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(attachment),
                'res_model': 'res.documents',
                'res_id': res_id,
            })
            return attachment_id

    @http.route(['/my/profile'], type='http', auth="user", website=True)
    def my_profile(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        values = {'emp': emp}
        return request.render("website_portal.my_profile", values)

    @http.route(['''/my/profile/edit/<model('hr.employee'):emp>''','/my/profile/edit'], type='http', auth="user", website=True, methods=['POST','GET'])
    def my_profile_edit(self,emp=None, **kw):
        if not kw:
            user = request.env.user
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],limit=1)
            accessibles = request.env['accessible.emp.info'].sudo().search(['|',('available_for', '=', 'all_employees'),('employees_ids', 'in', emp.id)]).mapped('tab_name')
            values = {'emp': emp,'accessibles': accessibles}
            return request.render("website_portal.my_profile_edit", values)
        else:
            if 'country2_id' in kw:
                kw['country2_id'] = int(kw['country2_id'])
            if 'country_of_birth' in kw:
                kw['country_of_birth'] = int(kw['country_of_birth'])
            if 'country_id' in kw:
                kw['country_id'] = int(kw['country_id'])
            if 'passport_country_id' in kw:
                kw['passport_country_id'] = int(kw['passport_country_id'])
            emp.sudo().write(kw)
            emp_link = "/my/profile/edit/%s" % (emp.id)
            return werkzeug.utils.redirect(emp_link)
        
    @http.route(['/my/documents'], type='http', auth="user", website=True)
    def my_documents(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1).id
        documents = request.env['res.documents'].sudo().search([('employee_id', '=', emp)])
        values = {
            'documents': documents,
            'page_name': 'Documents',
            'default_url': '/my/documents',
        }
        return request.render("website_portal.my_documents", values)

    @http.route(['''/my/document/view/<model('res.documents'):document>'''], type='http', auth="user", website=True)
    def my_documents_view(self, document, **kw):
        user = request.env.user
        default_values = {}
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],limit=1)
        default_values['issue_date'] = document.issue_date
        default_values['expiry_date'] = document.expiry_date
        default_values['issue_place'] = document.issue_place
        return request.render(
            "website_portal.my_documents_view", {
                'document': document,
                'page_name': 'document','default_values': default_values,
                'emp_id': emp and emp.id or False
            })

    @http.route(['''/my/document/<model('res.documents'):document>'''], type='http', auth="user", website=True)
    def my_documents_upload(self, document, **kw):
        user = request.env.user
        default_values = {}
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],limit=1)
        default_values['issue_date'] = document.issue_date
        default_values['expiry_date'] = document.expiry_date
        default_values['issue_place'] = document.issue_place
        return request.render(
            "website_portal.my_documents_upload", {
                'document': document,
                'page_name': 'document','default_values': default_values,
                'emp_id': emp and emp.id or False
            })


    @http.route(['/my/documents/upload/<int:id>'], type='http', auth="user", website=True, methods=['POST'])
    def my_documents_upload_att(self,id, **kw):
        if 'attachment' in request.params:
            attached_files = request.httprequest.files.getlist('attachment')
            document = request.env['res.documents'].sudo().search([('id', '=', id)],limit=1)
            for attachment in attached_files:
                attachment_id = self.attachment_format(document.id, attachment)
                document.update({
                    'attachment_ids': [(4, attachment_id.id)],
                })
            del kw['attachment']
            # issue_date = str(kw['issue_date']).split('/')
            # issue_date = issue_date[2] + issue_date[1] + issue_date[0]
            # issue_date = datetime.strptime(str(issue_date), '%Y%m%d').date()
            # expiry_date = str(kw['expiry_date']).split('/')
            # expiry_date = expiry_date[2] + expiry_date[1] + expiry_date[0]
            # expiry_date = datetime.strptime(str(expiry_date), '%Y%m%d').date()
            document.sudo().write(kw)
            return request.redirect("/my/documents")
                # attached_file =  self.prepare_attachment(attachment)
                # res.documents
                # print(attached_file)
        #         attached_file = attachment.read()
        #         print(attached_file)
        # user = request.env.user
        # emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
        #                                                limit=1).id
        # documents = request.env['res.documents'].sudo().search([('employee_id', '=', emp)])
        # values = {
        #     'documents': documents,
        #     'page_name': 'Documents',
        #     'default_url': '/my/documents',
        # }
        # return request.render("website_portal.my_documents", values)
