# -*- encoding: utf-8 -*-

from odoo import models, tools, fields, api, _
import base64
import binascii


class ProductImages(models.Model):
    _name = "product.image"

    image = fields.Binary(string="Image", required=True)
    product_image_preview = fields.Many2one('product.image.preview', string='Property Images')

    @api.onchange('image')
    @api.constrains('image')
    def _get_onclick_image(self):
        for product in self:
            if product.image:
                product.display_image = product.image

    display_image = fields.Binary(attachment=True)
    name = fields.Char(string="Name", default='Property Images')
    product_id = fields.Many2one('product.template', string='Product')


class ProductImagesPreview(models.Model):
    _name = "product.image.preview"

    name = fields.Char(string='Property Images',default='Property Images')
    image_id = fields.Many2one('product.image', string='Property Images')
    image_ids = fields.One2many('product.image', 'product_image_preview', string='Property Images')
    image_preview = fields.Binary(string="Image", required=True)
    product_id = fields.Many2one('product.template', string='Product')

    def action_image_preview(self):
        self.image_ids = self.image_ids - self.image_id
        if self.image_ids:
            self.image_id = self.image_ids[0]
            self.image_preview = self.image_id.image
        else:
            self.image_ids = [(6, 0, self.product_id.image_ids.ids)]
            self.image_id = self.image_ids[0]
            self.image_preview = self.image_id.image
