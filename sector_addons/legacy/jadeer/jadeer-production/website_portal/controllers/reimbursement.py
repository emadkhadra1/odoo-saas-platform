# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessDenied, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR
import werkzeug
import base64


class ReimbursementPortal(CustomerPortal):

    def get_attachment(self, attachment, expense):
        data = {
            'res_name': attachment.filename,
            'res_model': 'hr.expense',
            'res_id': expense,
            'datas': base64.encodestring(attachment.read()),
            'type': 'binary',
            'name': attachment.filename,
        }
        return data

    @http.route(['''/my/reimbursement/edit/<model('hr.expense'):reimbursement>'''], type='http', auth="user", website=True, methods=['POST','GET'])
    def my_reimbursement_edit(self,reimbursement, **kw):
        if not kw:
            user = request.env.user
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            attachment_obj = http.request.env['ir.attachment']
            attachment_ids = attachment_obj.sudo().search([('res_model', '=', 'hr.expense'),('res_id', '=', reimbursement.id)])
            products = http.request.env['product.product'].sudo().search(
                [('can_be_expensed', '=', True)])
            currencies = http.request.env['res.currency'].sudo().search([])
            taxes = http.request.env['account.tax'].sudo().search([('type_tax_use', '=', 'purchase')])
            return request.render(
                "website_portal.portal_my_reimbursement_edit", {
                    'reimbursement': reimbursement,
                    'attachment_ids': attachment_ids,
                    'page_name': 'Reimbursement',
                    'taxes': taxes,  'currencies': currencies, 'products': products,
                    'emp_id': emp and emp.id or False
                })
        else:
            kw['employee_id'] = http.request.env.user.employee_id.id
            kw['currency_id'] = int(kw['currency_id'])
            kw['product_id'] = int(kw['product_id'])
            if 'attachment_1' in request.params:
                attachment_1 = kw['attachment_1']
                del kw['attachment_1']
            if 'attachment_2' in request.params:
                attachment_2 = kw['attachment_2']
                del kw['attachment_2']
            if 'attachment_3' in request.params:
                attachment_3 = kw['attachment_3']
                del kw['attachment_3']
            if 'attachment_4' in request.params:
                attachment_4 = kw['attachment_4']
                del kw['attachment_4']
            if 'attachment_5' in request.params:
                attachment_5 = kw['attachment_5']
                del kw['attachment_5']
            if 'attachment_6' in request.params:
                attachment_6 = kw['attachment_6']
                del kw['attachment_6']
            if 'attachment_7' in request.params:
                attachment_7 = kw['attachment_7']
                del kw['attachment_7']
            if 'attachment_8' in request.params:
                attachment_8 = kw['attachment_8']
                del kw['attachment_8']
            if 'attachment_9' in request.params:
                attachment_9 = kw['attachment_9']
                del kw['attachment_9']
            if 'attachment_10' in request.params:
                attachment_10 = kw['attachment_10']
                del kw['attachment_10']
            if 'tax_ids' in request.params:
                taxes = kw['tax_ids']
                del kw['tax_ids']

            expense = reimbursement.sudo().write(kw)
            if 'tax_ids' in request.params:
                tax_ids = request.httprequest.form.getlist('tax_ids')

                # for tax in tax_ids:
                tax_ids = list(map(int, tax_ids))
                reimbursement.sudo().update({
                    'tax_ids': [(6,0, tax_ids)],
                })
            attachment_obj = http.request.env['ir.attachment']
            if 'attachment_1' in request.params:
                if attachment_1:
                    attachments = self.get_attachment(attachment_1, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_2' in request.params:
                if attachment_2:
                    attachments = self.get_attachment(attachment_2, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_3' in request.params:
                if attachment_3:
                    attachments = self.get_attachment(attachment_3, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_4' in request.params:
                if attachment_4:
                    attachments = self.get_attachment(attachment_4, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_5' in request.params:
                if attachment_5:
                    attachments = self.get_attachment(attachment_5, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_6' in request.params:
                if attachment_6:
                    attachments = self.get_attachment(attachment_6, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_7' in request.params:
                if attachment_7:
                    attachments = self.get_attachment(attachment_7, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_8' in request.params:
                if attachment_8:
                    attachments = self.get_attachment(attachment_8, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_9' in request.params:
                if attachment_9:
                    attachments = self.get_attachment(attachment_9, reimbursement)
                    attachment_obj.sudo().create(attachments)
            if 'attachment_10' in request.params:
                if attachment_10:
                    attachments = self.get_attachment(attachment_10, reimbursement)
                    attachment_obj.sudo().create(attachments)
            pd_link = "/my/reimbursement/%s" % (reimbursement.id)
            return werkzeug.utils.redirect(pd_link)

    @http.route(['''/my/reimbursement/delete/<model('hr.expense'):reimbursement>'''], type='http', methods=['GET'],
                auth="user", website=True,
                csrf=False)
    def portal_my_reimbursement_delete(self, reimbursement, **kw):
        reimbursement.sudo().unlink()
        return werkzeug.utils.redirect('/my/reimbursement')

    @http.route(['''/my/reimbursement/to_submit/<model('hr.expense'):reimbursement>'''], type='http', methods=['GET'],
                auth="user", website=True,
                csrf=False)
    def portal_my_reimbursement_to_submit(self, reimbursement, **kw):
        # reimbursement.sudo().write({'state':'reported'})
        reimbursement.sudo().action_submit_expenses()
        return werkzeug.utils.redirect('/my/reimbursement')

    @http.route('/my/reimbursement/submit', type='http', auth="public", website=True)
    def website_reimbursement_form(self, **kwargs):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1).id
        products = http.request.env['product.product'].sudo().search(
            [('can_be_expensed', '=', True)])
        currencies = http.request.env['res.currency'].sudo().search([])
        taxes = http.request.env['account.tax'].sudo().search([('type_tax_use', '=', 'purchase')])
        return request.render("website_portal.reimbursement_submit",
                              {'taxes': taxes,  'currencies': currencies, 'products': products,
                               'page_name': 'reimbursement_new'})

    @http.route(['/reimbursement/insert'], type='http', auth="public", methods=['POST'], website=True)
    def reimbursement_submitted(self, **kw):
        if not (http.request.env.user.employee_id):
            raise AccessDenied()
        kw['employee_id'] = http.request.env.user.employee_id.id
        kw['currency_id'] = int(kw['currency_id'])
        kw['product_id'] = int(kw['product_id'])
        if 'attachment_1' in request.params:
            attachment_1 = kw['attachment_1']
            del kw['attachment_1']
        if 'attachment_2' in request.params:
            attachment_2 = kw['attachment_2']
            del kw['attachment_2']
        if 'attachment_3' in request.params:
            attachment_3 = kw['attachment_3']
            del kw['attachment_3']
        if 'attachment_4' in request.params:
            attachment_4 = kw['attachment_4']
            del kw['attachment_4']
        if 'attachment_5' in request.params:
            attachment_5 = kw['attachment_5']
            del kw['attachment_5']
        if 'attachment_6' in request.params:
            attachment_6 = kw['attachment_6']
            del kw['attachment_6']
        if 'attachment_7' in request.params:
            attachment_7 = kw['attachment_7']
            del kw['attachment_7']
        if 'attachment_8' in request.params:
            attachment_8 = kw['attachment_8']
            del kw['attachment_8']
        if 'attachment_9' in request.params:
            attachment_9 = kw['attachment_9']
            del kw['attachment_9']
        if 'attachment_10' in request.params:
            attachment_10 = kw['attachment_10']
            del kw['attachment_10']
        if 'tax_ids' in request.params:
            taxes = kw['tax_ids']
            del kw['tax_ids']

        expense = request.env['hr.expense'].sudo().create(kw)
        if 'tax_ids' in request.params:
            tax_ids = request.httprequest.form.getlist('tax_ids')
            for tax in tax_ids:
                expense.update({
                    'tax_ids': [(4, int(tax))],
                })
        attachment_obj = http.request.env['ir.attachment']
        if 'attachment_1' in request.params:
            if attachment_1:
                attachments = self.get_attachment(attachment_1, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_2' in request.params:
            if attachment_2:
                attachments = self.get_attachment(attachment_2, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_3' in request.params:
            if attachment_3:
                attachments = self.get_attachment(attachment_3, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_4' in request.params:
            if attachment_4:
                attachments = self.get_attachment(attachment_4, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_5' in request.params:
            if attachment_5:
                attachments = self.get_attachment(attachment_5, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_6' in request.params:
            if attachment_6:
                attachments = self.get_attachment(attachment_6, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_7' in request.params:
            if attachment_7:
                attachments = self.get_attachment(attachment_7, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_8' in request.params:
            if attachment_8:
                attachments = self.get_attachment(attachment_8, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_9' in request.params:
            if attachment_9:
                attachments = self.get_attachment(attachment_9, expense)
                attachment_obj.sudo().create(attachments)
        if 'attachment_10' in request.params:
            if attachment_10:
                attachments = self.get_attachment(attachment_10, expense)
                attachment_obj.sudo().create(attachments)
        pd_link = "/my/reimbursement/%s" % (expense.id)
        return werkzeug.utils.redirect(pd_link)

    @http.route(['''/my/reimbursement/<model('hr.expense'):reimbursement>'''], type='http', auth="user", website=True)
    def portal_my_reimbursement(self, reimbursement, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        attachment_obj = http.request.env['ir.attachment']
        attachment_ids = attachment_obj.sudo().search([('res_model', '=', 'hr.expense'),
                                                       ('res_id', '=', reimbursement.id)])
        return request.render(
            "website_portal.portal_my_reimbursement", {
                'reimbursement': reimbursement,
                'attachment_ids': attachment_ids,
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
            'page_name': 'reimbursement',
            'default_url': '/my/reimbursement',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'search': search,
        })
        return request.render("website_portal.portal_reimbursement", values)
