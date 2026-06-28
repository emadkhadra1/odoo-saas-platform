# -*- coding: utf-8 -*-
from odoo import http

# class ConstructionBudgeting(http.Controller):
#     @http.route('/construction_budgeting/construction_budgeting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/construction_budgeting/construction_budgeting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('construction_budgeting.listing', {
#             'root': '/construction_budgeting/construction_budgeting',
#             'objects': http.request.env['construction_budgeting.construction_budgeting'].search([]),
#         })

#     @http.route('/construction_budgeting/construction_budgeting/objects/<model("construction_budgeting.construction_budgeting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('construction_budgeting.object', {
#             'object': obj
#         })