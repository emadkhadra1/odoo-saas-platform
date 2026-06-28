# -*- coding: utf-8 -*-

import math

from odoo import http, _, fields, models
from odoo.http import request
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv.expression import OR
from collections import OrderedDict
from operator import itemgetter
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.tools.translate import _

import werkzeug

# class website_account(website_account):
class CustomerPortal(CustomerPortal):

    def _get_allocations_searchbar_sortings(self):
        return {
            'date_from': {'label': _('Date From'), 'order': 'create_date desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

    # list route
    @http.route(['/my/allocation', '/my/allocation/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_allocations(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = {}  # self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        allocation = request.env['hr.leave.allocation']
        employee = request.env['hr.employee'].sudo().search([('user_id', '=',request.env.user.id)], limit=1)
        domain = []  # self._prepare_quotations_domain(partner)
        domain +=['|',('employee_id', '=', employee[0].id),('employee_ids', '=', employee[0].id)]
        searchbar_sortings = self._get_allocations_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date_from'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        trip_count = allocation.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/allocation",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=trip_count,
            page=page,
            step=10
        )
        # search the count to display, according to the pager data
        trips = allocation.search(domain, order=sort_order, limit=10, offset=pager['offset'])
        request.session['my_allocations_history'] = trips.ids[:10]

        values.update({
            'date': date_begin,
            'allocations': trips.sudo(),
            'page_name': 'Allocation',
            'pager': pager,
            'default_url': '/my/allocation',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'employee':employee
        })
        return request.render("website_portal.portal_my_allocations", values)

    @http.route('''/my/allocation/submit''', type='http', auth="user", website=True)
    def portal_my_allocation_create(self, **kwargs):
        default_values = {}
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        emps = request.env['hr.employee'].sudo().search([('user_id', '!=', user.id)])
        holiday_domain = ([])

        allocation_type_ids = request.env['hr.leave.type'].search([])
        val_list = []
        for allocation in allocation_type_ids:
            val_list.append({'id':allocation.id,'name':allocation.name,})

        return request.render("website_portal.allocation_request_submit", {
            'holiday_types': val_list,
            'page_name': 'new_allocation', 'default_values': default_values, 'emps': emps})
    #
    @http.route(['''/my/allocation/<model('hr.leave.allocation'):trip>'''], type='http', auth="user", website=True)
    def portal_my_allocations_view(self, trip, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {
            'allocation': trip,
            'page_name': 'allocation',
            'emp_id': emp and emp.id or False
        }
        return request.render(
            "website_portal.portal_my_allocations_view", values)
    @http.route(['''/my/allocation/confirm/<model('hr.leave.allocation'):allocation>'''], type='http', methods=['GET'], auth="user",
                website=True,
                csrf=False)
    def portal_my_allocations_confirm(self, allocation, **kw):
        allocation.sudo().action_confirm()
        return request.redirect('/my/allocation')
