# -*- encoding: utf-8 -*-

from odoo import models, tools, fields, api, _
import base64
import binascii


class ProductImages(models.Model):
    _name = "project.image"

    image = fields.Binary(string="Image", required=True)
    project_image_preview = fields.Many2one('project.image.preview', string='Project Images')

    @api.onchange('image')
    @api.constrains('image')
    def _get_onclick_image(self):
        for project in self:
            if project.image:
                project.display_image = project.image

    display_image = fields.Binary(attachment=True)
    name = fields.Char(string="Name", default='Project Images')
    project_id = fields.Many2one('real.estate.project', string='Project')


class ProductImagesPreview(models.Model):
    _name = "project.image.preview"

    name = fields.Char(string='Project Images',default='Project Images')
    image_id = fields.Many2one('project.image', string='Project Images')
    image_ids = fields.One2many('project.image', 'project_image_preview', string='Project Images')
    image_preview = fields.Binary(string="Image", required=True)
    project_id = fields.Many2one('real.estate.project', string='Project')

    def action_image_preview(self):
        self.image_ids = self.image_ids - self.image_id
        if self.image_ids:
            self.image_id = self.image_ids[0]
            self.image_preview = self.image_id.image
        else:
            self.image_ids = [(6, 0, self.project_id.image_ids.ids)]
            self.image_id = self.image_ids[0]
            self.image_preview = self.image_id.image

# class projectattachments(models.Model):
#     _name = "project.other.attachment"
#
#     name = fields.Char(string='Description')
#     file_id = fields.Many2one('ir.attachment', string='File')
#     project_id = fields.Many2one('real.estate.project', string='Project')


