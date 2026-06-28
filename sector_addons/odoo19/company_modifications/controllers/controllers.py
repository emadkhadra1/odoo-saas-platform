# -*- coding: utf-8 -*-
from odoo import http

# class CompanyModifications(http.Controller):
#     @http.route('/company_modifications/company_modifications/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/company_modifications/company_modifications/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('company_modifications.listing', {
#             'root': '/company_modifications/company_modifications',
#             'objects': http.request.env['company_modifications.company_modifications'].search([]),
#         })

#     @http.route('/company_modifications/company_modifications/objects/<model("company_modifications.company_modifications"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('company_modifications.object', {
#             'object': obj
#         })