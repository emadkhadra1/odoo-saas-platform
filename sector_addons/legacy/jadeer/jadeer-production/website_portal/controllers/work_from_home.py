# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from collections import OrderedDict
from datetime import datetime

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Response
from odoo.tools import image_process
from odoo.tools.translate import _
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager


class CustomerPortal(portal.CustomerPortal):

    def prepare_attachment(self, attach):
        encoded = None
        filename = None
        if attach:
            filename = attach.filename
            attachment = attach
            attachment = attachment.read()
            encoded = base64.b64encode(attachment)
        return encoded

    def _get_permit_searchbar_sortings(self):
        return {
            'Create Date': {'label': _('Create Date'), 'order': 'create_date'},
            'Status': {'label': _('Status'), 'order': 'state'},
        }

    # list route
    @http.route(['/my/permit-request', '/my/permit-request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_permit_request(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = {}  # self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        permitRequest = request.env['hr.permit.request']

        domain = [('request_type','=','work_home')]   # self._prepare_quotations_domain(partner)

        searchbar_sortings = self._get_permit_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'Create Date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        permit_count = permitRequest.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/permit-request",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=permit_count,
            page=page,
            step=10
        )
        # search the count to display, according to the pager data
        permits = permitRequest.search(domain, order=sort_order, limit=10, offset=pager['offset'])
        request.session['my_permits_history'] = permits.ids[:10]

        values.update({
            'date': date_begin,
            'permits': permits.sudo(),
            'page_name': 'permitRequest',
            'pager': pager,
            'default_url': '/my/permit-request',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_portal.portal_my_permit_request", values)

    # form route
    @http.route('/my/permit-request/new', type='http', auth="public", website=True)
    def portal_my_permit_request_new(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1).id
        emps = request.env['hr.employee'].sudo().search([('user_id', '!=', user.id)])
        if kw:
            document = self.prepare_attachment(kw['document'])
            kw['document'] = document[1] if kw['document'] else False
            kw['employee_id'] = emp
            kw['request_type'] = 'work_home'
            # kw['delegate_id'] = int(kw['delegate_id'])
            http.request.env['hr.permit.request'].sudo().create(kw)
            return request.redirect("/my/permit-request")
        else:
            return request.render("website_portal.portal_my_permit_request_new",
                                  {'page_name': 'NewpermitRequest','emps': emps})

    # delete route
    @http.route(['''/my/permit-request/delete/<model('hr.permit.request'):permit>'''], type='http', methods=['GET'],
                auth="user", website=True, csrf=False)
    def portal_my_permit_request_delete(self, permit, **kw):
        permit.unlink()
        return request.redirect("/my/permit-request")

    # view route
    @http.route(['''/my/permit-request/<model('hr.permit.request'):permit>'''], type='http', auth="user", website=True)
    def portal_my_permit_request_view(self, permit, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {
                'permit': permit,
                'page_name': 'permitRequest',
                'emp_id': emp and emp.id or False
            }
        # history = request.session.get('my_permit_request_history', [])
        # values.update(self.get_records_pager(history, trip))
        return request.render(
            "website_portal.portal_my_permit_request_view", values)

    # edit route
    @http.route(['''/my/permit-request/edit/<model('hr.permit.request'):permit>'''], type='http', auth="user", website=True, methods=['POST','GET'])
    def portal_my_permit_request_edit(self,permit, **kw):
        if not kw:
            user = request.env.user
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            emps = request.env['hr.employee'].sudo().search([('user_id', '!=', user.id)])
            return request.render(
                "website_portal.portal_my_permit_request_edit", {
                    'permit': permit,
                    'emps': emps,
                    'page_name': 'permitRequest',
                    'emp_id': emp and emp.id or False
                })
        else:
            if 'document' in kw :
                document = self.prepare_attachment(kw['document'])
                kw['document'] = document[1]  if kw['document'] else False
            kw['delegate_employee_id'] = int(kw['delegate_employee_id'])
            permit.write(kw)
            return request.redirect("/my/permit-request")

    @http.route(['''/my/permit-request/submit/<model('hr.permit.request'):permit>'''], type='http', methods=['GET'],
                auth="user", website=True,
                csrf=False)
    def portal_my_permit_request_submit(self, permit, **kw):
        permit.sudo().write({'state': 'submit'})
        return request.redirect("/my/permit-request")

    @http.route(['/web/content/<string:model>/<int:id>/<string:field>'], type='http',auth="user")
    def portal_my_permit_request_download(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        return request.env['ir.http'].sudo()._get_content_common(xmlid=xmlid, model=model, res_id=id, field=field,
                                                          unique=unique, filename=filename,
                                                          filename_field=filename_field, download=download,
                                                          mimetype=mimetype, access_token=access_token, token=token)