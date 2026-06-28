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


# class website_account(website_account):
class CustomerPortal(CustomerPortal):

    def _get_loan_searchbar_sortings(self):
        return {
            'date': {'label': _('Date From'), 'order': 'date desc'},
            'Status': {'label': _('Status'), 'order': 'state'},
        }

    # list route
    @http.route(['/my/loan', '/my/loan/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loans(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = {}  # self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        loan = request.env['hr.loan']
        employee = request.env['hr.employee'].sudo().search([('user_id', '=',request.env.user.id)], limit=1)
        domain = []  # self._prepare_quotations_domain(partner)
        domain +=[('employee_id', '=', employee[0].id)]
        searchbar_sortings = self._get_loan_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        trip_count = loan.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/loan",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=trip_count,
            page=page,
            step=10
        )
        # search the count to display, according to the pager data
        trips = loan.search(domain, order=sort_order, limit=10, offset=pager['offset'])
        request.session['my_loans_history'] = trips.ids[:10]

        values.update({
            'date': date_begin,
            'loans': trips.sudo(),
            'page_name': 'loan',
            'pager': pager,
            'default_url': '/my/loan',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_portal.portal_my_loans", values)

    @http.route('''/my/loan/submit''', type='http', auth="user", website=True)
    def portal_my_loan_create(self, **kwargs):
        default_values = {}
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        emps = request.env['hr.employee'].sudo().search([('user_id', '!=', user.id)])
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
            # loan_types =  http.request.env['loan.type'].sudo().search(['&', ('virtual_remaining_loans', '>', 0), '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),'&',('allocation_type', '=', 'fixed'), ('max_loans', '>', '0')])
            # loan_types =  loan_types.with_context({},employee_id=request.env.user.employee_id.id)
            # loan_types =  loan_types.name_get()
        loan_domain = []
        loan_type_ids = request.env['loan.type'].search(loan_domain)
        val_list = []
        for loan in loan_type_ids:
            val_list.append({'id':loan.id,'name':loan.name,})

        return request.render("website_portal.loan_request_submit", {
            'loan_types': val_list,
            'page_name': 'new_loan', 'default_values': default_values, 'emps': emps})

    @http.route(['''/my/loan/<model('hr.loan'):trip>'''], type='http', auth="user", website=True)
    def portal_my_loans_view(self, trip, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {
            'loan': trip,
            'page_name': 'loan',
            'emp_id': emp and emp.id or False
        }
        return request.render(
            "website_portal.portal_my_loans_view", values)
