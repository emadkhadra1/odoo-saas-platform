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

    # def get_records_pager(self,ids, current):
    #     if current.id in ids :
    #         attr_name = 'access_url'
    #         idx = ids.index(current.id)
    #         return {
    #             'prev_record': idx != 0  ,
    #             'next_record': idx < len(ids) - 1 and getattr(current.browse(ids[idx + 1])),
    #         }
    #     return {}

    def _get_trip_searchbar_sortings(self):
        return {
            'date': {'label': _('Date From'), 'order': 'date_from desc'},
            'Status': {'label': _('Status'), 'order': 'state'},
        }

    # list route
    @http.route(['/my/business-trip', '/my/business-trip/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_business_trip(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = {}  # self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        BusinessTrip = request.env['business.trip.request']

        domain = []  # self._prepare_quotations_domain(partner)

        searchbar_sortings = self._get_trip_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        trip_count = BusinessTrip.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/business-trip",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=trip_count,
            page=page,
            step=10
        )
        # search the count to display, according to the pager data
        trips = BusinessTrip.search(domain, order=sort_order, limit=10, offset=pager['offset'])
        request.session['my_business_trip_history'] = trips.ids[:10]

        values.update({
            'date': date_begin,
            'trips': trips.sudo(),
            'page_name': 'BusinessTrip',
            'pager': pager,
            'default_url': '/my/business-trip',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_portal.portal_my_business_trip", values)

    # form route
    @http.route('/my/business-trip/new', type='http', auth="public", website=True)
    def portal_my_business_trip_new(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1).id
        if kw:
            document = self.prepare_attachment(kw['document'])
            kw['document'] = document[1] if kw['document'] else False
            kw['employee_id'] = emp
            http.request.env['business.trip.request'].sudo().create(kw)
            return request.redirect("/my/business-trip")
        else:
            return request.render("website_portal.portal_my_business_trip_new",
                                  {'page_name': 'NewBusinessTrip'})

    # delete route
    @http.route(['''/my/business-trip/delete/<model('business.trip.request'):trip>'''], type='http', methods=['GET'],
                auth="user", website=True, csrf=False)
    def portal_my_business_trip_delete(self, trip, **kw):
        trip.unlink()
        return request.redirect("/my/business-trip")

    # view route
    @http.route(['''/my/business-trip/<model('business.trip.request'):trip>'''], type='http', auth="user", website=True)
    def portal_my_business_trip_view(self, trip, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {
                'trip': trip,
                'page_name': 'BusinessTrip',
                'emp_id': emp and emp.id or False
            }
        # history = request.session.get('my_business_trip_history', [])
        # values.update(self.get_records_pager(history, trip))
        return request.render(
            "website_portal.portal_my_business_trip_view", values)

    # edit route
    @http.route(['''/my/business-trip/edit/<model('business.trip.request'):trip>'''], type='http', auth="user", website=True, methods=['POST','GET'])
    def portal_my_business_trip_edit(self,trip, **kw):
        if not kw:
            user = request.env.user
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            return request.render(
                "website_portal.portal_my_business_trip_edit", {
                    'trip': trip,
                    'page_name': 'BusinessTrip',
                    'emp_id': emp and emp.id or False
                })
        else:
            if 'document' in kw :
                document = self.prepare_attachment(kw['document'])
                kw['document'] = document[1]  if kw['document'] else False
            trip.write(kw)
            return request.redirect("/my/business-trip")

    @http.route(['''/my/business-trip/submit/<model('business.trip.request'):trip>'''], type='http', methods=['GET'],
                auth="user", website=True,
                csrf=False)
    def portal_my_business_trip_submit(self, trip, **kw):
        trip.sudo().button_submit()
        return request.redirect("/my/business-trip")

    @http.route(['/web/content/<string:model>/<int:id>/<string:field>'], type='http',auth="user")
    def portal_my_business_trip_download(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        return request.env['ir.http'].sudo()._get_content_common(xmlid=xmlid, model=model, res_id=id, field=field,
                                                          unique=unique, filename=filename,
                                                          filename_field=filename_field, download=download,
                                                          mimetype=mimetype, access_token=access_token, token=token)