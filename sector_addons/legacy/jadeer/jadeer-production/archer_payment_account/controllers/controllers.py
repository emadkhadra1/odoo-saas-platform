# -*- coding: utf-8 -*-
# from odoo import http


# class ArcherPaymentAccount(http.Controller):
#     @http.route('/archer_payment_account/archer_payment_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/archer_payment_account/archer_payment_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('archer_payment_account.listing', {
#             'root': '/archer_payment_account/archer_payment_account',
#             'objects': http.request.env['archer_payment_account.archer_payment_account'].search([]),
#         })

#     @http.route('/archer_payment_account/archer_payment_account/objects/<model("archer_payment_account.archer_payment_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('archer_payment_account.object', {
#             'object': obj
#         })
