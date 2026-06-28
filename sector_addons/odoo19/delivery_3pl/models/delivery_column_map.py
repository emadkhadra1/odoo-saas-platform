from odoo import models, fields, api

SYSTEM_FIELDS_SELECTION = [
    ('_ignore_', '--- تجاهل هذا العمود / Ignore ---'),
    # Rider identification
    ('rider_account_id', 'معرف الحساب (Rider Account ID)'),
    ('rider_name', 'اسم الحساب / الاسم الكامل (Rider Name)'),
    ('rider_user', 'مستخدم الحساب (Account User)'),
    ('rider_phone', 'هاتف المندوب (Rider Phone)'),
    ('plate_number', 'رقم اللوحة (Plate Number)'),
    # Vehicle
    ('vehicle_type_company', 'نوع المركبة - شركة (Vehicle Type Company)'),
    ('vehicle_type_contract', 'نوع المركبة - عقد (Vehicle Type Contract)'),
    # Targets
    ('platform_target', 'تارجت المنصة (Platform Target)'),
    ('company_target_val', 'تارجت الشركة (Company Target)'),
    # Orders
    ('accepted_tasks', 'مهام مقبولة (Accepted Tasks)'),
    ('delivered_tasks', 'مهام مسلمة / طلبات مسلمة (Delivered Tasks)'),
    ('large_orders_completed', 'طلبات كبيرة مكتملة (Large Orders)'),
    ('cancelled_tasks', 'مهام ملغاة (Cancelled Tasks)'),
    ('rejected_tasks', 'مهام مرفوضة (Rejected Tasks)'),
    ('driver_rejected', 'مرفوضة بالسائق (Driver Rejected)'),
    ('auto_rejected', 'مرفوضة تلقائياً (Auto Rejected)'),
    # Hours
    ('online_hours', 'ساعات أونلاين (Online Hours)'),
    ('peak_hours', 'ساعات الذروة (Peak Hours)'),
    # Performance rates
    ('ontime_rate', 'نسبة التسليم في الوقت (On-Time Rate)'),
    ('large_ontime_rate', 'نسبة طلبات كبيرة في الوقت (Large OTD)'),
    ('avg_delivery_duration', 'متوسط مدة التوصيل (Avg Duration)'),
    ('over_55min_rate', 'نسبة أكثر من 55 دقيقة (Over 55min)'),
    ('late_tasks', 'مهام متأخرة (Late Tasks)'),
    ('very_late_tasks', 'مهام متأخرة جداً (Very Late)'),
    ('on_time_deliveries', 'توصيلات في الوقت - عدد (On-Time Count)'),
    ('advance_deliveries', 'توصيلات مسبقة - عدد (Advance Count)'),
    # Monthly summary financials
    ('capacity_incentive', 'حافز السعة (Capacity Incentive)'),
    ('experience_incentive', 'حافز الخبرة (Experience Incentive)'),
    ('subsidy', 'إعانة (Subsidy)'),
    ('dxg', 'DXG'),
    ('tips_excl_vat', 'بقشيش بدون ضريبة (Tips excl. VAT)'),
    ('other_activities', 'أنشطة ومكافآت أخرى (Other Activities)'),
    ('deductions', 'خصومات (Deductions)'),
    ('food_damage_compensation', 'تعويض تلف طعام (Food Damage)'),
    ('other_adjustment', 'تعديل آخر (Other Adjustment)'),
    ('valid_days', 'الأيام الصالحة (Valid Days)'),
    # Order details
    ('order_id', 'رقم الطلب (Order ID)'),
    ('order_date', 'تاريخ الطلب (Order Date)'),
    ('city_name', 'المدينة (City)'),
    ('distance', 'المسافة بالكيلومتر (Distance KM)'),
    ('platform_amount', 'مبلغ المنصة (Platform Amount)'),
    # Fuel
    ('fuel', 'بنزين (Fuel)'),
    # Free text extra
    ('_extra_', 'حقل إضافي (Store as Extra Data)'),
]


class DeliveryColumnMap(models.Model):
    _name = 'delivery.column.map'
    _description = 'Excel Column Mapping per Contract (ربط أعمدة الاكسل)'
    _order = 'contract_id, sequence, id'

    contract_id = fields.Many2one(
        'delivery.contract', string='Contract', required=True,
        ondelete='cascade', index=True)
    sequence = fields.Integer(string='Seq', default=10)
    excel_column = fields.Char(
        string='Excel Column Header', required=True,
        help='اسم العمود كما يظهر في الملف (الحرف الأول والأخير يُطابقان بالضبط)\n'
             'Exact column header text as it appears in the Excel file.')
    system_field = fields.Selection(
        SYSTEM_FIELDS_SELECTION, string='System Field (الحقل في النظام)',
        help='الحقل في النظام الذي سيُخزن فيه هذا العمود.\n'
             'اختر "حقل إضافي" إذا أردت حفظ القيمة بدون ربط محدد.\n'
             'اختر "تجاهل" لتخطي هذا العمود تماماً.')
    custom_key = fields.Char(
        string='Extra Key (مفتاح إضافي)',
        help='إذا اخترت "حقل إضافي"، يُخزن هنا اسم المفتاح في extra_data.\n'
             'يُملأ تلقائياً من اسم العمود إذا تُرك فارغاً.')
    is_auto_detected = fields.Boolean(string='Auto-Detected', default=False,
                                      help='Detected automatically from file headers')
    notes = fields.Char(string='Notes')

    def name_get(self):
        result = []
        field_labels = dict(SYSTEM_FIELDS_SELECTION)
        for rec in self:
            field_label = field_labels.get(rec.system_field or '', '?')
            result.append((rec.id, f'"{rec.excel_column}" → {field_label}'))
        return result

    @api.onchange('excel_column')
    def _onchange_excel_column(self):
        if self.excel_column and not self.custom_key:
            self.custom_key = self.excel_column.strip().replace(' ', '_').lower()
