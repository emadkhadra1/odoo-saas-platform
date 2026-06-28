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

class PDPortal(CustomerPortal):

    @http.route(['/my/pd', '/my/pd/page/<int:page>'], type='http', auth="user", website=True)
    def my_pd(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content',
                         **kw):
        values = self._prepare_portal_layout_values()
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'pd_activity'},
        }
        searchbar_inputs = {
            'pd': {'input': 'pd_activity', 'label': _('Search <span class="nolabel"> (in PD)</span>')},
            'id': {'input': 'id', 'label': _('Search ID')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)],
                                                       limit=1)
        domain.append(('employee_id', '=', emp.id))
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        # archive_groups = self._get_archive_groups('helpdesk.ticket', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('pd_activity', 'all'):
                search_domain = OR([search_domain, [('pd_activity', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain

        # pager
        pd_count = request.env['pd.request'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/pd",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=pd_count,
            page=page,
            step=self._items_per_page
        )
        pds = request.env['pd.request'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_pd_history'] = pds.ids[:100]

        values.update({
            'date': date_begin,
            'pds': pds,
            'page_name': 'pd_request',
            'default_url': '/my/pd',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("website_portal.portal_pd", values)

    @http.route('/my/pd/submit', type='http', auth="public", website=True)
    def website_pd_form(self, **kwargs):
        return request.render("website_portal.pd_submit", {'page_name': 'pd_request_new' })


    @http.route(['''/my/pd/<model('pd.request'):pd>'''], type='http', auth="user", website=True)
    def portal_my_pd(self, pd, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        attachment_obj = http.request.env['ir.attachment']
        attachment_ids = attachment_obj.sudo().search([('res_model','=','pd.request'),
                                                      ('res_id','=', pd.id )])
        return request.render(
            "website_portal.portal_my_pd", {
                'pd': pd,
                'attachment_ids': attachment_ids,
                'page_name': 'my_pd',
                'emp_id': emp and emp.id or False
            })

    @http.route(['''/my/pd/delete/<model('pd.request'):pd>'''], type='http', methods=['GET'], auth="user", website=True,
     csrf=False)
    def portal_my_pd_delete(self, pd, **kw):
        pd.sudo().unlink()
        return werkzeug.utils.redirect('/my/pd')

    @http.route(['''/my/pd/edit/<model('pd.request'):pd>'''], type='http', auth="user", website=True, methods=['POST','GET'])
    def my_pd_edit(self,pd, **kw):
        if not kw:
            user = request.env.user
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            attachment_obj = http.request.env['ir.attachment']
            attachment_ids = attachment_obj.sudo().search([('res_model', '=', 'pd.request'),
                                                           ('res_id', '=', pd.id)])
            return request.render(
                "website_portal.portal_my_pd_edit", {
                    'pd': pd,
                    'attachment_ids': attachment_ids,
                    'page_name': 'PD Request',
                    'emp_id': emp and emp.id or False
                })
        else:

            pd.sudo().write(kw)
            if 'attachment' in request.params:
                del kw['attachment']
                attachment_list = request.httprequest.files.getlist('attachment')
                for attachment in attachment_list:
                    # if attachment:
                    attachments = {
                        'res_name': attachment.filename,
                        'res_model': 'pd.request',
                        'res_id': pd,
                        'datas': base64.encodestring(attachment.read()),
                        'type': 'binary',
                        'name': attachment.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attachment_obj.sudo().create(attachments)
            pd_link = "/my/pd/%s" % (pd.id)
            return werkzeug.utils.redirect(pd_link)


    @http.route(['/pd/pd_insert'], type='http', auth="public", methods=['POST'], website=True)
    def pd_submitted(self, **kw):
        if not (http.request.env.user.employee_id):
            raise AccessDenied()
        kw['employee_id'] = http.request.env.user.employee_id.id
        if 'attachment' in request.params:
            del kw['attachment']
        pd = http.request.env['pd.request'].sudo().create(kw)
        if 'attachment' in request.params:
            attachment_list = request.httprequest.files.getlist('attachment')
            for attachment in attachment_list:
                # if attachment:
                attachments = {
                           'res_name': attachment.filename,
                           'res_model': 'pd.request',
                           'res_id': pd,
                           'datas': base64.encodestring(attachment.read()),
                           'type': 'binary',
                           'name': attachment.filename,
                       }
                attachment_obj = http.request.env['ir.attachment']
                attachment_obj.sudo().create(attachments)
        pd_link = "/my/pd/%s" % (pd.id)
        return werkzeug.utils.redirect(pd_link)








    # js  request
    # @http.route(['''/pd/insert_data'''], type='json', auth="public", methods=['POST', 'GET'], website=True,
    #             csrf=False)
    # def website_pd_insert(self, **kwargs):
    #     if not (http.request.env.user.employee_id):
    #         raise AccessDenied()
    #     user = http.request.env.user
    #     # self = http.request.sudo()
    #     # try:
    #     print(kwargs)
    #     print(request.httprequest.data)
    #     attachment = kwargs.get('files')
    #     print("attachment")
    #     print(attachment)
    #     print("attachment")
    #     values = {
    #
    #         'employee_id': http.request.env.user.employee_id.id,
    #         'date_from': kwargs.get('from'),
    #         'date_to': kwargs.get('to'),
    #         'grade_level': kwargs.get('grade'),
    #         'pd_activity': kwargs.get('pd_activity'),
    #         'location_institution': kwargs.get('location'),
    #         'additional_cost': kwargs.get('add_cost'),
    #         'cost': kwargs.get('cost'),
    #         'knowledge_description': kwargs.get('knowledge'),
    #         'quality_description': kwargs.get('quality'),
    #         'brief_explanation': kwargs.get('brief'),
    #
    #     }
    #     pd = http.request.env['pd.request'].sudo().create(values)
    #
    #
    #     attachment_id = self.attachment_format(pd.id, attachment)
    #     print(attachment_id)
    #     if attachment_id:
    #         pd.update({
    #             'attachment_ids': [(4, attachment_id.id)],
    #         })
    #     return {
    #         'id': pd.id
    #     }

