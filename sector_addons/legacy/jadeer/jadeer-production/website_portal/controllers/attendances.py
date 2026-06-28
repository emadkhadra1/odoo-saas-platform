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

    def _get_attendance_searchbar_sortings(self):
        return {
            'date': {'label': _('Date From'), 'order': 'check_in desc'},
            'Status': {'label': _('Status'), 'order': 'state'},
        }

    # list route
    @http.route(['/my/attendances', '/my/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = {}  # self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Attendance = request.env['hr.attendance']
        employee = request.env['hr.employee'].sudo().search([('user_id', '=',request.env.user.id)], limit=1)
        domain = []  # self._prepare_quotations_domain(partner)
        domain +=[('employee_id', '=', employee[0].id)]
        searchbar_sortings = self._get_attendance_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        trip_count = Attendance.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=trip_count,
            page=page,
            step=10
        )
        # search the count to display, according to the pager data
        trips = Attendance.search(domain, order=sort_order, limit=10, offset=pager['offset'])
        request.session['my_attendances_history'] = trips.ids[:10]

        values.update({
            'date': date_begin,
            'attendances': trips.sudo(),
            'page_name': 'Attendance',
            'pager': pager,
            'default_url': '/my/attendances',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_portal.portal_my_attendances", values)

    # view route
    @http.route(['''/my/attendances/<model('hr.attendance'):trip>'''], type='http', auth="user", website=True)
    def portal_my_attendances_view(self, trip, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {
            'attendance': trip,
            'page_name': 'Attendance',
            'emp_id': emp and emp.id or False
        }
        return request.render(
            "website_portal.portal_my_attendances_view", values)
