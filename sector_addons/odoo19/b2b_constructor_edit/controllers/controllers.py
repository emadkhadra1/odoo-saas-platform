# -*- coding: utf-8 -*-
from odoo import http

# class B2bConstructorEdit(http.Controller):
#     @http.route('/b2b_constructor_edit/b2b_constructor_edit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/b2b_constructor_edit/b2b_constructor_edit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('b2b_constructor_edit.listing', {
#             'root': '/b2b_constructor_edit/b2b_constructor_edit',
#             'objects': http.request.env['b2b_constructor_edit.b2b_constructor_edit'].search([]),
#         })

#     @http.route('/b2b_constructor_edit/b2b_constructor_edit/objects/<model("b2b_constructor_edit.b2b_constructor_edit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('b2b_constructor_edit.object', {
#             'object': obj
#         })