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

    def get_domain_my_leaves(self, user):
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg

    def _document_check_accesss(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user
        holidays = request.env['hr.leave']
        holidays_count = holidays.sudo().search_count([
            ('user_id', 'child_of', [request.env.user.id]),
            # ('type','=','remove')
        ])
        values.update({
            'holidays_count': holidays_count,
        })
        return values

    @http.route(['''/my/leave/<model('hr.leave'):timeoff>'''], type='http', auth="user", website=True)
    def portal_my_timeoff(self, timeoff, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        holiday_domain = ([])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        return request.render(
            "website_portal.portal_my_leave", {
                'timeoff': timeoff,
                'holiday_types': holiday_type_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
                'page_name': 'leave',
                'emp_id': emp and emp.id or False
            })

    @http.route('''/my/leaves/submit''', type='http', auth="user", website=True)
    def portal_my_leave_create(self, **kwargs):
        default_values = {}
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        emps = request.env['hr.employee'].sudo().search([('user_id', '!=', user.id)])
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
            # leave_types =  http.request.env['hr.leave.type'].sudo().search(['&', ('virtual_remaining_leaves', '>', 0), '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),'&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')])
            # leave_types =  leave_types.with_context({},employee_id=request.env.user.employee_id.id)
            # leave_types =  leave_types.name_get()
        holiday_domain = (['|', ('requires_allocation', '=', 'no'), ('has_valid_allocation', '=', True)])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        return request.render("website_portal.leave_request_submit", {
            'leave_types': holiday_type_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
            'page_name': 'new_leave', 'default_values': default_values, 'emps': emps})

    @http.route('/leave_request_form', type='http', auth="user", methods=['POST'], website=True)
    def leave_request_form(self, **kwargs):
        kwargs['employee_id'] = request.env.user.employee_id.id
        kwargs['holiday_status_id'] = int(kwargs['holiday_status_id'])
        request_date_from = str(kwargs['request_date_from']).split('/')
        request_date_from = request_date_from[2] + request_date_from[1] + request_date_from[0]
        request_date_to = str(kwargs['request_date_to']).split('/')
        request_date_to = request_date_to[2] + request_date_to[1] + request_date_to[0]
        kwargs['request_date_from'] = datetime.strptime(str(request_date_from), '%Y%m%d').date()
        kwargs['request_date_to'] = datetime.strptime(str(request_date_to), '%Y%m%d').date()
        tmp_leave = request.env['hr.leave'].sudo().new(kwargs)
        tmp_leave._onchange_request_parameters()

        values = tmp_leave._convert_to_write(tmp_leave._cache)
        try:
            leave = request.env['hr.leave'].sudo().create(values)

            message = 'You Request Has Been Sent Successfully, Thank you.'
        # except ValidationError:
        #     default_values = {}
        #     leave_types =  http.request.env['hr.leave.type'].sudo().search(['&', ('virtual_remaining_leaves', '>', 0), '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),'&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')])
        #     leave_types =  leave_types.with_context({},employee_id=request.env.user.employee_id.id)
        #     leave_types =  leave_types.name_get()
        #     default_values['holiday_status_id'] = int(kwargs['holiday_status_id'])
        #     return request.render("website_portal.leave_request_submit",
        #                           {'leave_types':leave_types,'default_values': default_values ,'message': ValidationError})
        # raise ValidationError(self.prepare_error_msg(e))
        # leave = request.env['hr.leave'].sudo().create(kwargs)
        except Exception as e:
            # raise ValidationError(self.prepare_error_msg(e))
            return request.render("website_portal.display_leave_request",
                                  {'message': self.prepare_error_msg(e)})
        return request.render("website_portal.display_leave_request",
                              {'leave': leave, 'message': message})

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave']
        Timeoff_sudo = request.env['hr.leave'].sudo()
        domain = self.get_domain_my_leaves(request.env.user)

        # holiday_domain=(['&', ('virtual_remaining_leaves', '>', 0),
        #                 '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),
        #                 '&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')
        #                 ])
        # holiday_type_ids = request.env['hr.leave.type'].sudo().search(holiday_domain)
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        # values.update({
        #     'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get()})
        # fileter  By
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'confirm': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            'validate1': {'label': _('Second Approval'), 'domain': [('state', '=', 'validate1')]},
            'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
        # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'timeoff': {'input': 'timeoff', 'label': _('Time Off Type')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )
        # default groupby
        if groupby == 'timeoff':
            order = "holiday_status_id, %s" % order
        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_timeoff = []
            if leaves:
                grouped_timeoff = [leaves]
        else:
            grouped_timeoff = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(leaves, itemgetter('holiday_status_id'))]
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'grouped_timeoff': grouped_timeoff,
            'page_name': 'leave',
            'default_url': '/my/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("website_portal.portal_my_leaves_details", values)

    @http.route(['/my/leavesdd', '/my/leavesdd/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leave_request(self, page=1, sortby=None, search=None, search_in='all', **kw):
        # if not request.env.user.has_group('website_portal.group_employee_leave'):
        #     # return request.render("odoo_timesheet_portal_user_employee.not_allowed_leave_request")
        #     return request.render("website_portal.not_allowed_leave_request")
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        holidays_obj = http.request.env['hr.leave']
        domain = [
            ('employee_id', '=', request.env.user.employee_id.id),
        ]
        # count for pager
        holidays_count = http.request.env['hr.leave'].sudo().search_count(domain)
        # pager
        # pager = request.website.pager(
        pager = portal_pager(
            url="/my/leaves",
            total=holidays_count,
            page=page,
            step=self._items_per_page
        )
        sortings = {
            'date': {'label': _('Newest'), 'order': 'state,request_date_from desc'},
        }
        searchbar_sortings = {
            'date': {'label': _('Request Date'), 'order': 'request_date_from desc'},

            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_input = {
            'input': {'label': _('Request Date'), 'input': 'request_date_from'},

            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Description')},
            'holiday_status_id': {'input': 'holiday_status_id', 'label': _('Search in Holiday Type')},
            # 'state': {'input': 'state', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        # search
        domain_mng = []
        domain_ch = []
        if search and search_in:
            search_domain = []
            # if search_in in ('state', 'all'):
            #     search_domain = OR([search_domain, [('state', 'ilike', search),]])
            if search_in in ('holiday_status_id', 'all'):
                search_domain = OR([search_domain, [('holiday_status_id', 'ilike', search), ]])
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search), ]])

            domain += search_domain
            domain_ch += search_domain
            domain_mng += search_domain

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        holidays = holidays_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'holidays': holidays,
            'page_name': 'leave',
            'sortings': sortings,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
            'pager': pager,
            'default_url': '/my/leave_request',
        })
        return request.render("website_portal.portal_my_leaves_details", values)

    @http.route(['/my/leaves/summary'], type='http', auth="user", website=True)
    def leaves_summary(self):
        get_days_all_request = request.env['hr.leave.type'].sudo().get_days_all_request()
        return request.render(
            "website_portal.my_leaves_summary", {'page_name': 'leave',
                                                 'timeoffs': get_days_all_request})
