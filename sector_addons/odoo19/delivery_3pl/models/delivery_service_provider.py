from odoo import models, fields, api


class DeliveryServiceProvider(models.Model):
    _name = 'delivery.service.provider'
    _description = 'شركة مزودة خدمة (Service Provider Company)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='اسم الشركة المزودة', required=True, tracking=True)
    monthly_fee_per_rider = fields.Float(
        string='المبلغ الشهري لكل مندوب (ريال)',
        digits=(12, 2),
        default=0.0,
        tracking=True,
        help='المبلغ الذي تحتفظ به الشركة من مستحقات كل مندوب فرى لانسر شهرياً.',
    )
    phone = fields.Char(string='الهاتف', tracking=True)
    email = fields.Char(string='البريد الإلكتروني')
    contact_person = fields.Char(string='الشخص المسؤول', tracking=True)
    active = fields.Boolean(string='نشط', default=True)
    notes = fields.Text(string='ملاحظات')

    rider_ids = fields.One2many(
        'delivery.rider', 'service_provider_id',
        string='المناديب المرتبطون',
    )
    rider_count = fields.Integer(
        string='عدد المناديب',
        compute='_compute_rider_count',
        store=True,
    )

    @api.depends('rider_ids')
    def _compute_rider_count(self):
        for rec in self:
            rec.rider_count = len(rec.rider_ids)
