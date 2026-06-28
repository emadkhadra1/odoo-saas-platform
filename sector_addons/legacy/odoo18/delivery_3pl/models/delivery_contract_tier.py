from odoo import models, fields, api


class DeliveryContractTier(models.Model):
    """
    شريحة تسعير مرنة مرتبطة بالعقد.
    تحل محل الحقول الثابتة A/B/C/D وتسمح بعدد غير محدود من الشرائح.

    منطق الشريحة:
    - إذا حققت الشركة عدد مناديب صالحين (Valid DAs) بين الحد الأدنى والأقصى لهذه الشريحة
    - يحصل كل مندوب صالح على: (سعر الطلب × عدد طلباته)
    """
    _name = 'delivery.contract.tier'
    _description = 'Contract Pricing Tier (شريحة تسعير العقد)'
    _order = 'sequence, min_company_valid_das desc'

    contract_id = fields.Many2one(
        'delivery.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='اسم الشريحة / Tier Name',
        required=True,
        help='مثال: شريحة A، شريحة B، ...',
    )
    sequence = fields.Integer(string='Sequence', default=10)

    min_company_valid_das = fields.Integer(
        string='الحد الأدنى للمناديب الصالحين / Min Valid DAs',
        default=0,
        help='الحد الأدنى من المناديب الصالحين في الشركة لتحقيق هذه الشريحة.\n'
             'Minimum valid DAs the company must achieve for this tier to apply.',
    )
    max_company_valid_das = fields.Integer(
        string='الحد الأقصى / Max Valid DAs (0 = غير محدود)',
        default=0,
        help='الحد الأقصى (اترك 0 لغير المحدود).\n'
             '0 = unlimited. Tier applies when valid_das is between min and max.',
    )

    price_per_order_bike = fields.Float(
        string='سعر الطلب - دراجة (ريال) / Price/Order Bike (SAR)',
        digits=(12, 2),
        default=0.0,
        help='المبلغ لكل طلب للمندوب الصالح الذي يستخدم دراجة.',
    )
    price_per_order_car = fields.Float(
        string='سعر الطلب - سيارة (ريال) / Price/Order Car (SAR)',
        digits=(12, 2),
        default=0.0,
        help='المبلغ لكل طلب للمندوب الصالح الذي يستخدم سيارة.',
    )

    notes = fields.Char(string='ملاحظات / Notes')

    def name_get(self):
        result = []
        for rec in self:
            max_label = str(rec.max_company_valid_das) if rec.max_company_valid_das else '∞'
            label = f"{rec.name}  ({rec.min_company_valid_das} – {max_label} DA)"
            result.append((rec.id, label))
        return result

    def matches(self, valid_das_count):
        """Returns True if valid_das_count falls within this tier's range."""
        self.ensure_one()
        if valid_das_count < self.min_company_valid_das:
            return False
        if self.max_company_valid_das and valid_das_count > self.max_company_valid_das:
            return False
        return True
