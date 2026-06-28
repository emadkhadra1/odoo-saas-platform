# -*- coding: utf-8 -*-
from odoo import http

# class FinancialCustody(http.Controller):
#     @http.route('/financial_custody/financial_custody/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financial_custody/financial_custody/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financial_custody.listing', {
#             'root': '/financial_custody/financial_custody',
#             'objects': http.request.env['financial_custody.financial_custody'].search([]),
#         })

#     @http.route('/financial_custody/financial_custody/objects/<model("financial_custody.financial_custody"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financial_custody.object', {
#             'object': obj
#         })