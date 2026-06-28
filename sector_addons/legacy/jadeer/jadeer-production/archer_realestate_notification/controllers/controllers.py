# -*- coding: utf-8 -*-
# from odoo import http


# class ArcherRealestateNotification(http.Controller):
#     @http.route('/archer_realestate_notification/archer_realestate_notification', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/archer_realestate_notification/archer_realestate_notification/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('archer_realestate_notification.listing', {
#             'root': '/archer_realestate_notification/archer_realestate_notification',
#             'objects': http.request.env['archer_realestate_notification.archer_realestate_notification'].search([]),
#         })

#     @http.route('/archer_realestate_notification/archer_realestate_notification/objects/<model("archer_realestate_notification.archer_realestate_notification"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('archer_realestate_notification.object', {
#             'object': obj
#         })
