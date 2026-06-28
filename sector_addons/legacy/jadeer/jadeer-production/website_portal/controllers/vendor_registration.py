# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from werkzeug.exceptions import NotFound
import werkzeug
import base64


class WebsiteVendorRegistration(http.Controller):

    def prepare_attachment(self, attach):
        encoded = None
        filename = None
        if attach:
            filename = attach.filename
            attachment = attach
            attachment = attachment.read()
            encoded = base64.b64encode(attachment)
        return encoded

    @http.route('/vendor-registration/submit', type='http', auth="public", website=True, methods=['POST', 'GET'],
                csrf=False)
    def vendor_registration(self, **kw):

        comm_reg = self.prepare_attachment(kw['comm_reg'])
        tax_reg = self.prepare_attachment(kw['tax_reg'])
        gosi = self.prepare_attachment(kw['gosi'])
        saudization = self.prepare_attachment(kw['saudization'])
        iban = self.prepare_attachment(kw['iban'])
        if 'partner_fields' in request.params:
            del kw['partner_fields']
        kw['comm_reg'] = comm_reg[1]  if kw['comm_reg'] else False
        kw['tax_reg'] = tax_reg[1]  if kw['tax_reg'] else False
        kw['gosi'] = gosi[1]  if kw['gosi'] else False
        kw['saudization'] = saudization[1]  if kw['saudization'] else False
        kw['iban'] = iban[1]  if kw['iban'] else False
        # kw['company_type'] = 'company'
        if 'pro_name' in request.params:
            del kw['pro_name']
        if 'description' in request.params:
            del kw['description']
        obj_id = http.request.env['vendor.registration'].sudo().create(kw)
        if 'partner_fields' in request.params:
            partner_fields = request.httprequest.form.getlist('partner_fields')
            for field in partner_fields:
                obj_id.update({
                    'partner_fields': [(4, int(field))],
                })
        pro_name = request.httprequest.form.getlist('pro_name')
        description = request.httprequest.form.getlist('description')
        if 'pro_name' in request.params:
            for idx, desc in enumerate(pro_name):
                if desc != "":
                    vals = {
                        'name': pro_name[idx],
                        'description': description[idx],
                        'registration_id': obj_id.id,
                    }
                    http.request.env['partner.portfolio'].sudo().create(vals)

        return request.redirect("/vendor_thankyou/vendor-registration-" + str(obj_id.id))


    @http.route(['''/vendor_thankyou/<model('vendor.registration'):vendor>'''], type='http', auth="public", website=True, methods=['POST','GET'],
     csrf=False)
    def vendor_registration_thankyou(self,vendor, **kw):
        return request.render("website_portal.vendor_thankyou",{'vendor':vendor.sudo()})

    @http.route('/vendor-registration-check', type='http', auth="public", website=True, methods=['POST', 'GET'])
    def vendor_registration_check(self, **kw):
        if kw :
            reg_status = http.request.env['vendor.registration'].sudo().search([('id','=',int(kw['check2'])),('comm_reg_id','=',kw['check1'])])
            if reg_status :
                return request.render("website_portal.vendor_registration_check",{'reg_status':reg_status})
            else:
                return request.render("website_portal.vendor_registration_check", {'reg_status': 'not_found'})
        return request.render("website_portal.vendor_registration_check")