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

    def _get_pay_searchbar_sortings(self):
        return {
            'date': {'label': _('Date From'), 'order': 'date_from desc'},
            'Status': {'label': _('Status'), 'order': 'state'},
        }

    # list route
    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = {}  # self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Payslip = request.env['hr.payslip']
        employee = request.env['hr.employee'].sudo().search([('user_id', '=',request.env.user.id)], limit=1)
        domain = []  # self._prepare_quotations_domain(partner)
        domain +=[('employee_id', '=', employee[0].id)]

        searchbar_sortings = self._get_pay_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        trip_count = Payslip.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/payslips",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=trip_count,
            page=page,
            step=10
        )
        # search the count to display, according to the pager data
        trips = Payslip.search(domain, order=sort_order, limit=10, offset=pager['offset'])
        request.session['my_payslips_history'] = trips.ids[:10]

        values.update({
            'date': date_begin,
            'payslips': trips.sudo(),
            'page_name': 'Payslip',
            'pager': pager,
            'default_url': '/my/payslips',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_portal.portal_my_payslips", values)

    # view route
    @http.route(['''/my/payslips/<model('hr.payslip'):trip>'''], type='http', auth="user", website=True)
    def portal_my_payslips_view(self, trip, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {
            'payslip': trip,
            'page_name': 'Payslip',
            'emp_id': emp and emp.id or False
        }
        return request.render(
            "website_portal.portal_my_payslips_view", values)
