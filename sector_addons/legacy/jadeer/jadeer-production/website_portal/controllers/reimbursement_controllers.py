# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR


class ReimbursementPortal(CustomerPortal):

    @http.route(['/my/pd', '/my/pd/page/<int:page>'], type='http', auth="user", website=True)
    def my_pd(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content',
                         **kw):
        values = self._prepare_portal_layout_values()
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
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
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = request.env['pd.request'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/reimbursement",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        expense = request.env['pd.request'].search(domain, order=order, limit=self._items_per_page,
                                                   offset=pager['offset'])
        request.session['my_expense_history'] = expense.ids[:100]

        values.update({
            'date': date_begin,
            'tickets': expense,
            'page_name': 'Reimbursement',
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
        return request.render("website_portal.pd_submit")


    @http.route('/my/reimbursement/submit', type='http', auth="public", website=True)
    def website_reimbursement_form(self, **kwargs):
        products = http.request.env['product.product'].sudo().search(
            [('can_be_expensed', '=', True)])

        return request.render("website_portal.reimbursement_submit", {'products': products})

    @http.route(['''/my/reimbursement/<model('hr.expense'):reimbursement>'''], type='http', auth="user", website=True)
    def portal_my_reimbursement(self, reimbursement, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        return request.render(
            "website_portal.portal_my_reimbursement", {
                'reimbursement': reimbursement,
                'page_name': 'Reimbursement',
                'emp_id': emp and emp.id or False
            })

    @http.route(['/my/reimbursement', '/my/reimbursement/page/<int:page>'], type='http', auth="user", website=True)
    def my_reimbursement(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content',
                         **kw):
        values = self._prepare_portal_layout_values()
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
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
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = request.env['hr.expense'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/reimbursement",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        expense = request.env['hr.expense'].search(domain, order=order, limit=self._items_per_page,
                                                   offset=pager['offset'])
        request.session['my_expense_history'] = expense.ids[:100]

        values.update({
            'date': date_begin,
            'tickets': expense,
            'page_name': 'Reimbursement',
            'default_url': '/my/reimbursement',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("website_portal.portal_reimbursement", values)
