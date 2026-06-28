from odoo import fields, models
from odoo.exceptions import ValidationError

class UpdatePrice(models.TransientModel):
    _name = 'update.price.wizard'

    update_type = fields.Selection(selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False, )
    update_percentage = fields.Float('percentage per meter',)
    update_amount = fields.Float('price per meter')
    unit_ids = fields.Many2many('product.template', required=True,domain=[('state','in',['sale','blocked']), ('is_residential', '=', True)])

    # unit_fields_ids = fields.Many2many('ir.model.fields', string='Unit Fields',
    #                                    domain=[('model', '=', 'product.template'), ('ttype', '!=',
    #                                                                                 ['one2many', 'many2one',
    #                                                                                  'datetime', 'boolean',
    #                                                                                  'selection',
    #                                                                                  'many2one_reference',
    #                                                                                  'many2many', 'html',
    #                                                                                  'text', 'binary', 'date',
    #                                                                                  'reference','char','monetary']),
    #                                            ('store', '=', True),
    #                                            ('related', '=', False)])
    # utility_ids = fields.Many2many('product.utility', string=' Unit Utility', )
    # utility_fields_ids = fields.Many2many('ir.model.fields', 'model_id', string='Utility Fields',
    #                                       domain=[('model', '=', 'product.utility'), ('ttype', '!=',
    #                                                                                   ['one2many', 'many2one',
    #                                                                                    'datetime', 'boolean',
    #                                                                                    'selection',
    #                                                                                    'many2one_reference',
    #                                                                                    'many2many', 'html',
    #                                                                                    'text', 'binary', 'date',
    #                                                                                    'reference','char','monetary']),
    #                                               ('store', '=', True),
    #                                               ('related', '=', False)])
    #
    attached_area_ids = fields.Many2many('attached.area.line', string=' Attached Area',
                                         )
    attach_area_update = fields.Boolean('Update Attached Area')
    unit_update = fields.Boolean('Update Unit')
    # attached_area_fields_ids = fields.Many2many('ir.model.fields', 'model_id', string='Attached Area Fields',
    #                                             domain=[('model', '=', 'attached.area.line'), ('ttype', '!=',
    #                                                                                            ['one2many', 'many2one',
    #                                                                                             'datetime', 'boolean',
    #                                                                                             'selection',
    #                                                                                             'many2one_reference',
    #                                                                                             'many2many', 'html',
    #                                                                                             'text', 'binary',
    #                                                                                             'date', 'reference','char','monetary']),
    #                                                     ('store', '=', True),
    #                                                     ('related', '=', False)])

    # def confirm(self):
    #     for rec in self:
    #         if rec.unit_fields_ids:
    #             for record in rec.unit_fields_ids:
    #                 if record.model == 'product.template':
    #                     value = record.name
    #                     if rec.update_type == 'percentage':
    #                         cr = self._cr
    #                         query = """update product_template set  "{value}" = "{value}"+ ("{value}" * {update_percentage} / 100.0)
    #                         """.format(value=value,
    #                                    update_percentage=rec.update_percentage) + " where id in (" + ",".join(
    #                             repr(v) for v in self.unit_ids.ids).replace("[", "").replace("]", "") + ")"
    #                         print(query)
    #                         cr.execute(query)
    #                     else:
    #                         cr = self._cr
    #                         query = """update product_template set  "{value}" = "{value}"+  + {update_amount}
    #                         """.format(value=value, update_amount=rec.update_amount) + " where id in (" + ",".join(
    #                             repr(v) for v in self.unit_ids.ids).replace("[", "").replace("]", "") + ")"
    #                         print(query)
    #                         cr.execute(query)
    #         if rec.utility_fields_ids and rec.utility_ids:
    #             for record in rec.utility_fields_ids:
    #                 if record.model == 'product.utility':
    #                     value = record.name
    #                     if rec.update_type == 'percentage':
    #                         cr = self._cr
    #                         query = """update product_utility set  "{value}" = "{value}"+ ("{value}" * {update_percentage} / 100.0)
    #                         """.format(value=value,
    #                                    update_percentage=rec.update_percentage) + " where id in (" + ",".join(
    #                             repr(v) for v in self.utility_ids.ids).replace("[", "").replace("]", "") + ")"
    #                         print(query)
    #                         cr.execute(query)
    #                     else:
    #                         cr = self._cr
    #                         query = """update product_utility set  "{value}" = "{value}"+  + {update_amount}
    #                         """.format(value=value, update_amount=rec.update_amount) + " where id in (" + ",".join(
    #                             repr(v) for v in self.utility_ids.ids).replace("[", "").replace("]", "") + ")"
    #                         print(query)
    #                         cr.execute(query)
    #         if rec.attached_area_fields_ids and rec.attached_area_ids:
    #             for record in rec.attached_area_fields_ids:
    #                 if record.model == 'attached.area.line':
    #                     value = record.name
    #                     if rec.update_type == 'percentage':
    #                         cr = self._cr
    #                         query = """update attached_area_line set  "{value}" = "{value}"+ ("{value}" * {update_percentage} / 100.0)
    #                         """.format(value=value,
    #                                    update_percentage=rec.update_percentage) + " where id in (" + ",".join(
    #                             repr(v) for v in self.attached_area_fields_ids.ids).replace("[", "").replace("]",
    #                                                                                                          "") + ")"
    #                         print(query)
    #                         cr.execute(query)
    #                     else:
    #                         cr = self._cr
    #                         query = """update attached_area_line set  "{value}" = "{value}"+  + {update_amount}
    #                         """.format(value=value, update_amount=rec.update_amount) + " where id in (" + ",".join(
    #                             repr(v) for v in self.attached_area_fields_ids.ids).replace("[", "").replace("]",
    #                                                                                                          "") + ")"
    #                         print(query)
    #                         cr.execute(query)



    def confirm(self):
        for rec in self:
            if not rec.unit_update and not rec.attach_area_update:
                raise  ValidationError('Please Select Update Area or update unit')
            # unit.write({record.name: dat[0].get(record.name) + (
            #         dat[0].get(record.name) * rec.update_percentage / 100.0)})
            if rec.unit_ids and rec.unit_update:
                for unit in rec.unit_ids:
                    if rec.update_type == 'amount' and rec.update_amount:
                        unit.write({'meter_price':unit.meter_price + rec.update_amount})
                    else:
                        unit.write({'meter_price':unit.meter_price + (unit.meter_price * rec.update_percentage / 100.0)})

            if rec.attached_area_ids and rec.attach_area_update:
                if rec.unit_ids:
                        for attached in rec.attached_area_ids :
                            if rec.update_type == 'amount' and rec.update_amount:
                                attached.write({'price':attached.price + rec.update_amount})
                            else:
                                attached.write({'price':attached.price + (attached.price * rec.update_percentage / 100.0)})
