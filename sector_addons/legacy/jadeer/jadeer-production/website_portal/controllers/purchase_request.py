# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError, AccessDenied
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR
import werkzeug
import base64


class PRPortal(CustomerPortal):

    @http.route(['/my/purchase_request', '/my/purchase_request/page/<int:page>'], type='http', auth="user", website=True)
    def my_pr(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content',
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

        domain.append(('create_uid', '=', request.env.user.id))
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
        pd_count = request.env['purchase.requisition.adi'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/purchase_request",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=pd_count,
            page=page,
            step=self._items_per_page
        )
        pds = request.env['purchase.requisition.adi'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_pd_history'] = pds.ids[:100]

        values.update({
            'date': date_begin,
            'pds': pds,
            'page_name': 'pr_request',
            'default_url': '/my/purchase_request',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            # 'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            # 'search_in': search_in,
            # 'search': search,
        })
        return request.render("website_portal.portal_pr", values)

    @http.route(['''/budget/account/search'''], type='json', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def analytic_search(self, budget_id=False, **kwargs):
        budget_lines_ids = http.request.env['crossovered.budget.lines'].sudo().search([('crossovered_budget_id', '=', budget_id)])
        account_analytic_ids = http.request.env['account.analytic.account'].sudo().search_read([('id', 'in', budget_lines_ids.ids)])
        account_account_ids = http.request.env['account.account'].sudo().search_read(
            [('id', 'in', budget_lines_ids.mapped('account_id').ids)])
        return {'analytic': account_analytic_ids, 'accounts': account_account_ids}

    @http.route('/my/purchase_request/submit', type='http', auth="public", website=True)
    def website_pr_form(self, **kwargs):

        budgt_account_ids =http.request.env['crossovered.budget'].sudo().search([]).crossovered_budget_line.account_id.ids
        account_analytic_id = http.request.env['account.analytic.account'].sudo().search([])
        account_id = http.request.env['account.account'].sudo().search([('id','in', budgt_account_ids)])
        field_id = http.request.env['partner.fields'].sudo().search([])
        vendors = http.request.env['res.partner'].sudo().search([('supplier_rank', '>', 0)])
        products = http.request.env['product.product'].sudo().search(
            [('purchase_ok', '=', True)])
        currencies = http.request.env['res.currency'].sudo().search([])
        return request.render("website_portal.pr_submit", {'products': products, 'budgets': [],
                                                           'currencies': currencies, 'account_analytic_ids': [],
                                                           'account_ids': account_id, 'field_ids': field_id,
                                                           'vendors': vendors, 'page_name': 'pr_request_new'})

    @http.route(['''/my/purchase_request/<model('purchase.requisition.adi'):pr>'''], type='http', auth="user", website=True)
    def portal_my_pr(self, pr, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        order_points = request.env['purchase.order.points'].sudo().search([('order_id.pr_id', '=', pr.id)], limit=1)
        return request.render(
            "website_portal.portal_my_pr", {
                'pr': pr,
                'order_points': order_points,
                'page_name': 'my_pr',
                'emp_id': emp and emp.id or False
            })

    @http.route(['/pr/point/receive_insert'], type='http', auth="public", methods=['POST'], website=True)
    def point_received(self, **kw):
        po_id = request.httprequest.form.get('po_select')
        pr_id = request.httprequest.form.get('pr_id')
        point_id = request.httprequest.form.get('point_select')
        received_qty = request.httprequest.form.get('receive_qty')
        action = request.httprequest.form.get('receive_pr_products_btn')
        vals={}
        if 'po_id' in request.params:
            del kw['po_id']
        if 'point_id' in request.params:
            del kw['point_id']
        if 'received_qty' in request.params:
            del kw['received_qty']
        vals={
            'po_id' : int(po_id),
            'pr_id': int(pr_id),
            'po_point_id':int(point_id),
            'received_qty':float(received_qty),
            'close_list': True if action == 'Receive & Close' else False

        }
        pr = http.request.env['purchase.requisition.receive.line.pr'].sudo().create(vals)
        pr_link = "/my/purchase_request/{}-{}/receive".format(pr.pr_id.name,pr.pr_id.id)
        return werkzeug.utils.redirect(pr_link)

    @http.route(['''/my/purchase_request/<model('purchase.requisition.adi'):pr>/receive'''], type='http', auth="user", website=True)
    def purchase_request_receive_products(self, pr, **kw):
        user = request.env.user
        orders = request.env['purchase.order'].sudo().search([('pr_id', '=', pr.id), ('state', '=', 'purchase'), ('points_ids', '!=', False)])
        order_points = request.env['purchase.order.points'].sudo().search([('order_id.pr_id', '=', pr.id)], limit=1)
        received_point_ids = request.env['purchase.requisition.receive.line.pr'].sudo().search_read([('pr_id', '=', pr.id)])
        return request.render(
            "website_portal.receive_pr_products", {
                'pr': pr,
                'orders': orders,
                'order_points': order_points,
                'received_point_ids':received_point_ids
            })

    @http.route(['''/my/purchase_request/receive/search/point'''], type='json', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def pr_points_search(self, po_id=False, sfrom=False, point_id=False, **kwargs):
        order_points = False
        received_qty = 0.0
        if sfrom == 'po':
            execlude_ids = []
            retr_order_points = request.env['purchase.order.points'].sudo().search([('order_id', '=', po_id)])
            for point in retr_order_points:
                received_point_ids = request.env['purchase.requisition.receive.line.pr'].sudo().search([('po_id', '=', po_id)])
                if received_point_ids:
                    received_sum = sum(received_point_ids.mapped('received_qty'))
                    if received_sum >= point.product_qty:
                        execlude_ids.append(point.id)
            order_points = request.env['purchase.order.points'].sudo().search_read([('id', 'not in', execlude_ids), ('order_id', '=', po_id)])
        if sfrom == 'point':
            point_id = request.env['purchase.order.points'].sudo().browse(point_id)
            received_point_ids = request.env['purchase.requisition.receive.line.pr'].sudo().search([('po_point_id', '=', point_id.id)])
            received_qty = sum(received_point_ids.mapped('received_qty'))
        return {'order_points': order_points, 'remin_qty': (point_id.product_qty if point_id else 0) - received_qty}

    @http.route(['''/my/purchase_request/delete/<model('purchase.requisition.adi'):pd>'''], type='http', methods=['GET'], auth="user",
                website=True,
                csrf=False)
    def portal_my_purchase_request_delete(self, pd, **kw):
        pd.sudo().unlink()
        return werkzeug.utils.redirect('/my/purchase_request')

    @http.route(['''/my/pd/edit/<model('purchase.requisition.adi'):pd>'''], type='http', auth="user", website=True, methods=['POST', 'GET'])
    def my_purchase_edit(self, pd, **kw):
        if not kw:
            user = request.env.user
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            attachment_obj = http.request.env['ir.attachment']
            attachment_ids = attachment_obj.sudo().search([('res_model', '=', 'purchase.requisition.adi'),
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
                        'res_model': 'purchase.requisition.adi',
                        'res_id': pd,
                        'datas': base64.encodestring(attachment.read()),
                        'type': 'binary',
                        'name': attachment.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attachment_obj.sudo().create(attachments)
            pd_link = "/my/pd/%s" % (pd.id)
            return werkzeug.utils.redirect(pd_link)

    @http.route(['/purchase_request/pr_insert'], type='http', auth="public", methods=['POST'], website=True)
    def pr_submitted(self, **kw):
        name = request.httprequest.form.getlist('name')
        product_qty = request.httprequest.form.getlist('product_qty')
        product_price = request.httprequest.form.getlist('product_price')
        product_id = request.httprequest.form.getlist('product_id')

        if 'product_id' in request.params:
            del kw['product_id']
        if 'product_price' in request.params:
            del kw['product_price']
        if 'product_qty' in request.params:
            del kw['product_qty']
        if 'name' in request.params:
            del kw['name']
        if not (http.request.env.user.employee_id):
            raise AccessDenied()
        kw['state'] = 'submitted'
        account_id = http.request.env['account.account'].sudo().search([('id','=', kw['account_id'])])
        budgt_account_ids =http.request.env['crossovered.budget'].sudo().search([('crossovered_budget_line.account_id','in',account_id.ids)])
        kw['budget_id'] = budgt_account_ids.id
        kw['analytic_account_id'] = budgt_account_ids.crossovered_budget_line.search([('crossovered_budget_id','in',budgt_account_ids.ids),('account_id','=',account_id.id)])[0].analytic_account_id.id
        pr = http.request.env['purchase.requisition.adi'].sudo().create(kw)

        if 'name' in request.params:
            for idx, desc in enumerate(name):
                if desc != "":
                    product = product_id[idx]
                    product_uom = request.env['product.product'].sudo().search([('id', '=', product)], limit=1).uom_id.id
                    vals = {
                        'requisition_id': pr.id,
                        'name': desc,
                        'product_id': product,
                        'product_uom': product_uom,
                        'product_price': float(product_price[idx]),
                        'product_qty': float(product_qty[idx]),
                    }
                    http.request.env['purchase.requisition.line.adi'].sudo().create(vals)
        pr_link = "/my/purchase_request/%s" % (pr.id)
        return werkzeug.utils.redirect(pr_link)
