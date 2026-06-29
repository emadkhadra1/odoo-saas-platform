from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class DeliveryContract(models.Model):
    _name = 'delivery.contract'
    _description = 'Company Contract (Versioned)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'company_id, version desc'

    company_id = fields.Many2one('delivery.company', string='Company', required=True, tracking=True, ondelete='cascade')
    branch_id = fields.Many2one('delivery.company.branch', string='Branch', tracking=True,
                                 domain="[('company_id', '=', company_id)]")
    contract_number = fields.Char(string='Contract Number', required=True, tracking=True)
    version = fields.Integer(string='Version', default=1, required=True, tracking=True)
    contract_type = fields.Selection([
        ('parcel', 'Parcel Contract (عقد طرود)'),
        ('service', 'Service Contract (عقد خدمات)'),
        ('other', 'Other'),
    ], string='Contract Type', default='parcel', required=True, tracking=True)

    rider_type = fields.Selection([
        ('all', 'الكل / All'),
        ('kafala', 'كفالة / Sponsored (Kafala)'),
        ('freelance', 'فري لانس / Freelance'),
    ], string='نوع المندوبين / Rider Type',
        default='all', required=True, tracking=True,
        help='يُستخدم للتمييز بين عقود الكفالة والفري لانس لنفس الشركة.\n'
             'يسمح النظام بعقد نشط واحد لكل نوع مندوب في نفس الفرع.',
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ], string='Status', default='draft', required=True, tracking=True)

    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    settlement_cycle = fields.Selection([
        ('weekly', 'Weekly'),
        ('semi_monthly', 'Semi-Monthly'),
        ('monthly', 'Monthly'),
    ], string='Settlement Cycle', default='monthly', required=True, tracking=True)
    commission_rate = fields.Float(string='Commission Rate (%)', digits=(5, 2), tracking=True)
    penalty_policy = fields.Text(string='Penalty Policy')
    deposit_policy = fields.Text(string='Deposit Policy')
    payment_terms_days = fields.Integer(string='Payment Terms (Days)', default=30)
    auto_renew = fields.Boolean(string='Auto-Renew', default=False)
    column_mapping = fields.Text(string='Excel Column Mapping (JSON)')
    notes = fields.Text(string='Notes')

    pricing_rule_ids = fields.One2many('delivery.pricing.rule', 'contract_id', string='Pricing Rules')
    pricing_rule_count = fields.Integer(compute='_compute_pricing_rule_count')
    settlement_ids = fields.One2many('delivery.settlement', 'contract_id', string='Settlements')
    import_session_ids = fields.One2many('delivery.import.session', 'contract_id', string='Import Sessions')
    validity_criteria_ids = fields.One2many('delivery.validity.criteria', 'contract_id', string='Validity Criteria')
    experience_config_ids = fields.One2many('delivery.experience.score.config', 'contract_id', string='Experience Score Config')
    company_target_ids = fields.One2many('delivery.company.target', 'contract_id', string='Company Targets')
    column_map_ids = fields.One2many('delivery.column.map', 'contract_id', string='Column Mapping')

    # ── نمط التسعير ────────────────────────────────────────────────────────────
    pricing_mode = fields.Selection([
        ('standard', 'متقدم — قواعد التسعير التقليدية (Advanced Pricing Rules)'),
        ('fixed_fee', 'رسوم شهرية ثابتة — هنقر فرى / جاهز / توجو (Fixed Monthly Fee)'),
        ('hungerstation_internal', 'كفالة هنقر — تارجيت 550 طلب + راتب (HungerStation Kafala)'),
        ('keeta', 'كيتا — 4 حالات (صالح/غير صالح × تارجيت/بدون تارجيت)'),
        ('tier_per_order', 'شرائح لكل طلب — النمط القديم (Legacy Tier Per Order)'),
    ], string='نمط التسعير / Pricing Mode',
        default='standard', required=True, tracking=True,
        help='اختر نمط التسعير المناسب للعقد:\n'
             '• رسوم شهرية ثابتة: للمنصات البسيطة (هنقر فرى/جاهز/توجو)\n'
             '• كفالة هنقر: تارجيت 550 طلب — راتب + تارجيت\n'
             '• كيتا: 4 حالات حسب الصلاحية وتحقيق التارجيت\n'
             '• شرائح لكل طلب: النمط القديم (للتوافق مع الإصدارات السابقة)\n'
             '• متقدم: للحالات المعقدة',
    )
    rider_monthly_fee = fields.Float(
        string='الرسوم الشهرية للمندوب (ريال) / Rider Monthly Fee (SAR)',
        digits=(12, 2),
        default=0.0,
        tracking=True,
        help='نمط "رسوم شهرية ثابتة": المبلغ الثابت الذي تحتفظ به الشركة من كل مندوب شهرياً.',
    )
    tier_ids = fields.One2many(
        'delivery.contract.tier', 'contract_id',
        string='شرائح التسعير / Pricing Tiers',
    )

    # ── الشركة المزودة للخدمة (للعقود الفرى) ────────────────────────────────
    service_provider_id = fields.Many2one(
        'delivery.service.provider',
        string='الشركة المزودة للخدمة',
        tracking=True,
        help='الشركة التي تزوّد المنادوب الفرى لانسر لهذا العقد. تُستخدم في احتساب صافي مزود الخدمة.',
    )

    # ── إعدادات كفالة هنقر ───────────────────────────────────────────────────
    hs_target_orders = fields.Integer(
        string='تارجيت هنقر (عدد الطلبات)',
        default=550,
        tracking=True,
        help='الحد الأدنى من الطلبات لتحقيق التارجيت والحصول على الراتب الأساسي + الإضافي.',
    )
    hs_base_salary = fields.Float(
        string='الراتب الأساسي عند التارجيت (ريال)',
        digits=(12, 2),
        default=1500.0,
        tracking=True,
        help='الراتب الأساسي الذي يُصرف عند تحقيق التارجيت (550 طلب).',
    )
    hs_rate_above_target = fields.Float(
        string='سعر الطلب الإضافي فوق التارجيت (ريال/طلب)',
        digits=(12, 2),
        default=8.0,
        tracking=True,
        help='سعر كل طلب إضافي فوق الـ 550 طلب.',
    )
    hs_rate_below_target = fields.Float(
        string='سعر الطلب عند عدم تحقيق التارجيت (ريال/طلب)',
        digits=(12, 2),
        default=4.0,
        tracking=True,
        help='سعر كل طلب إذا لم يتجاوز المندوب الـ 550 طلب.',
    )

    # ── إعدادات كيتا (4 حالات) ───────────────────────────────────────────────
    keeta_target_orders = fields.Integer(
        string='تارجيت كيتا (عدد الطلبات)',
        default=360,
        tracking=True,
        help='الحد الأدنى من الطلبات لتحقيق التارجيت الشخصي للمندوب.',
    )
    keeta_base_salary = fields.Float(
        string='الراتب الأساسي عند التارجيت (ريال)',
        digits=(12, 2),
        default=1500.0,
        tracking=True,
        help='الراتب الأساسي للمندوب الصالح الذي حقق التارجيت.',
    )
    keeta_extra_threshold = fields.Integer(
        string='الحد الثاني للطلبات الإضافية',
        default=400,
        tracking=True,
        help='فوق هذا الحد تتغير سعر الطلب الإضافي. مثال: 360–400 بـ 8 ريال، 400+ بـ 10 ريال.',
    )
    keeta_rate_extra_1 = fields.Float(
        string='سعر الطلب الإضافي (من التارجيت حتى الحد الثاني) (ريال)',
        digits=(12, 2),
        default=8.0,
        tracking=True,
        help='سعر كل طلب إضافي من 361 حتى 400 (الحد الثاني).',
    )
    keeta_rate_extra_2 = fields.Float(
        string='سعر الطلب الإضافي (فوق الحد الثاني) (ريال)',
        digits=(12, 2),
        default=10.0,
        tracking=True,
        help='سعر كل طلب إضافي فوق 400.',
    )
    keeta_company_bonus_pct = fields.Float(
        string='نسبة بونص تارجيت الشركة للمندوب (%)',
        digits=(5, 2),
        default=37.5,
        tracking=True,
        help='النسبة من بونص تارجيت الشركة التي تُوزَّع على المناديب الصالحين الذين حققوا التارجيت.',
    )
    keeta_tier_a_bonus = fields.Float(
        string='بونص الشريحة A (ريال)',
        digits=(12, 2),
        default=100.0,
        tracking=True,
        help='مكافأة إضافية للمندوب الواقع في الشريحة A.',
    )
    keeta_tier_b_penalty = fields.Float(
        string='خصم الشريحة B (ريال)',
        digits=(12, 2),
        default=300.0,
        tracking=True,
        help='خصم على المندوب الواقع في الشريحة B (يُخزَّن كقيمة موجبة ويُطرح من المستحقات).',
    )
    keeta_tier_c_penalty = fields.Float(
        string='خصم الشريحة C (ريال)',
        digits=(12, 2),
        default=500.0,
        tracking=True,
    )
    keeta_tier_d_penalty = fields.Float(
        string='خصم الشريحة D (ريال)',
        digits=(12, 2),
        default=1000.0,
        tracking=True,
    )
    keeta_valid_no_target_rate = fields.Float(
        string='سعر الطلب — صالح + لم يحقق التارجيت (ريال/طلب)',
        digits=(12, 2),
        default=4.0,
        tracking=True,
        help='حالة 2: المندوب صالح لكن لم يصل للتارجيت → عدد الطلبات × هذا السعر.',
    )
    keeta_invalid_target_rate = fields.Float(
        string='سعر الطلب — غير صالح + حقق التارجيت (ريال/طلب)',
        digits=(12, 2),
        default=4.0,
        tracking=True,
        help='حالة 3: المندوب غير صالح لكنه وصل للتارجيت → عدد الطلبات × هذا السعر.',
    )
    keeta_invalid_no_target_rate = fields.Float(
        string='سعر الطلب — غير صالح + لم يحقق التارجيت (ريال/طلب)',
        digits=(12, 2),
        default=2.0,
        tracking=True,
        help='حالة 4: المندوب غير صالح ولم يصل للتارجيت → عدد الطلبات × هذا السعر.',
    )

    display_name_computed = fields.Char(compute='_compute_display_name_computed', store=False)

    def _compute_pricing_rule_count(self):
        for rec in self:
            rec.pricing_rule_count = len(rec.pricing_rule_ids)

    @api.depends('contract_number', 'version', 'status', 'contract_type')
    def _compute_display_name_computed(self):
        for rec in self:
            type_label = dict(rec._fields['contract_type'].selection).get(rec.contract_type, '')
            rec.display_name_computed = f"{rec.contract_number} (v{rec.version}) - {rec.status} [{type_label}]"

    def name_get(self):
        result = []
        for rec in self:
            branch_label = f" [{rec.branch_id.branch_code}]" if rec.branch_id and rec.branch_id.branch_code else ""
            result.append((rec.id, f"{rec.contract_number}{branch_label} (v{rec.version})"))
        return result

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.branch_id = False
            return {'domain': {'branch_id': [('company_id', '=', self.company_id.id)]}}

    def action_activate(self):
        self.ensure_one()
        if self.status != 'draft':
            raise ValidationError('Only draft contracts can be activated.')
        domain = [
            ('company_id', '=', self.company_id.id),
            ('status', '=', 'active'),
            ('rider_type', '=', self.rider_type),
            ('id', '!=', self.id),
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        else:
            domain.append(('branch_id', '=', False))
        current_active = self.search(domain)
        current_active.write({'status': 'expired'})
        self.write({'status': 'active'})

    def action_terminate(self):
        self.ensure_one()
        if self.status != 'active':
            raise ValidationError('Only active contracts can be terminated.')
        self.write({'status': 'terminated'})

    def action_reactivate(self):
        """إعادة تفعيل عقد منتهٍ — يعيده إلى مسودة للمراجعة قبل التفعيل."""
        self.ensure_one()
        if self.status not in ('terminated', 'expired'):
            raise ValidationError('يمكن إعادة تفعيل العقود المنتهية أو المنتهية الصلاحية فقط.')
        self.write({'status': 'draft'})

    def action_renew(self):
        self.ensure_one()
        domain = [('company_id', '=', self.company_id.id)]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        max_version = max(self.search(domain).mapped('version') or [0])
        today = fields.Date.today()
        new_contract = self.copy({
            'version': max_version + 1,
            'status': 'draft',
            'start_date': today,
            'end_date': today + relativedelta(years=1),
            'notes': f'Renewed from v{self.version}',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.contract',
            'res_id': new_contract.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_default_rules(self):
        self.ensure_one()
        pricing_model = self.env['delivery.pricing.rule']
        slab_model = self.env['delivery.pricing.slab']
        level_model = self.env['delivery.incentive.level']
        validity_model = self.env['delivery.validity.criteria']
        experience_model = self.env['delivery.experience.score.config']

        today = fields.Date.today()
        base_vals = {
            'company_id': self.company_id.id,
            'branch_id': self.branch_id.id if self.branch_id else False,
            'contract_id': self.id,
            'effective_from': self.start_date or today,
            'effective_to': self.end_date or False,
        }

        if not self.pricing_rule_ids.filtered(lambda r: r.pricing_type == 'per_order'):
            pricing_model.create({
                **base_vals,
                'name': f'{self.company_id.name} - Per Order (لكل طلب)',
                'pricing_type': 'per_order',
                'vehicle_type': 'all',
                'base_amount': 8.00,
            })

        if not self.pricing_rule_ids.filtered(lambda r: r.pricing_type == 'tiered'):
            tiered = pricing_model.create({
                **base_vals,
                'name': f'{self.company_id.name} - Tiered Slabs (شرائح)',
                'pricing_type': 'tiered',
                'vehicle_type': 'all',
                'base_amount': 0,
                'is_active': False,
            })
            for seq, (f, t, p, label) in enumerate([
                (1, 200, 8.0, 'Base (أساسي)'),
                (201, 400, 10.0, 'Mid (متوسط)'),
                (401, 0, 12.0, 'Top (متقدم)'),
            ], 1):
                slab_model.create({
                    'pricing_rule_id': tiered.id,
                    'sequence': seq,
                    'from_orders': f,
                    'to_orders': t,
                    'price_per_order': p,
                    'label': label,
                })

        if not self.pricing_rule_ids.filtered(lambda r: r.pricing_type == 'fixed_salary'):
            pricing_model.create({
                **base_vals,
                'name': f'{self.company_id.name} - Fixed Salary (راتب ثابت)',
                'pricing_type': 'fixed_salary',
                'vehicle_type': 'all',
                'base_amount': 0,
                'daily_rate': 150.0,
                'working_days': 26,
                'fallback_per_order': 8.0,
                'bonus_threshold': 15,
                'bonus_per_order': 5.0,
                'is_active': False,
            })

        if not self.pricing_rule_ids.filtered(lambda r: r.pricing_type == 'per_distance'):
            pricing_model.create({
                **base_vals,
                'name': f'{self.company_id.name} - Per KM (لكل كم)',
                'pricing_type': 'per_distance',
                'vehicle_type': 'all',
                'base_amount': 6.0,
                'per_km_amount': 2.0,
                'km_start_from': 2,
                'max_km': 25,
                'is_active': False,
            })

        if not self.pricing_rule_ids.filtered(lambda r: r.pricing_type == 'experience_incentive'):
            exp_rule = pricing_model.create({
                **base_vals,
                'name': f'{self.company_id.name} - Experience Incentive (حافز الخبرة)',
                'pricing_type': 'experience_incentive',
                'vehicle_type': 'all',
                'base_amount': 0,
            })
            for seq, (lvl, rf, rt, bike, car) in enumerate([
                ('A', 0, 25, 2000, 2500),
                ('B', 25, 50, 1200, 2000),
                ('C', 50, 75, 900, 1700),
                ('D', 75, 100, 0, 0),
            ], 1):
                level_model.create({
                    'pricing_rule_id': exp_rule.id,
                    'sequence': seq,
                    'level': lvl,
                    'range_from': rf,
                    'range_to': rt,
                    'bike_amount': bike,
                    'car_amount': car,
                })

        if not self.pricing_rule_ids.filtered(lambda r: r.pricing_type == 'capacity_incentive'):
            cap_rule = pricing_model.create({
                **base_vals,
                'name': f'{self.company_id.name} - Capacity Incentive (حافز السعة)',
                'pricing_type': 'capacity_incentive',
                'vehicle_type': 'all',
                'base_amount': 0,
            })
            for seq, (lvl, rf, rt, bike, car) in enumerate([
                ('A', 120, 999, 2000, 2500),
                ('B', 100, 119, 1200, 2000),
                ('C', 90, 99, 900, 1700),
                ('D', 0, 89, 0, 0),
            ], 1):
                level_model.create({
                    'pricing_rule_id': cap_rule.id,
                    'sequence': seq,
                    'level': lvl,
                    'range_from': rf,
                    'range_to': rt,
                    'bike_amount': bike,
                    'car_amount': car,
                })

        if not self.validity_criteria_ids:
            validity_model.create({
                'contract_id': self.id,
                'branch_id': self.branch_id.id if self.branch_id else False,
                'company_id': self.company_id.id,
                'name': 'شروط الصلاحية الافتراضية',
                'min_daily_online_hours': 10.0,
                'min_valid_days': 26,
                'min_monthly_orders': 300,
                'must_attend_first_days': 3,
                'must_attend_last_days': 4,
                'must_attend_min_valid': 6,
            })

        if not self.experience_config_ids:
            experience_model.create({
                'contract_id': self.id,
                'branch_id': self.branch_id.id if self.branch_id else False,
                'company_id': self.company_id.id,
                'name': 'إعداد نقاط الخبرة الافتراضي',
                'on_time_delivery_weight': 38.0,
                'cancellation_rate_weight': 50.0,
                'advance_delivery_weight': 12.0,
                'min_orders_for_ranking': 100,
                'only_valid_da_eligible': True,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.contract',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.constrains('status', 'company_id', 'branch_id', 'rider_type')
    def _check_single_active(self):
        for rec in self:
            if rec.status == 'active':
                domain = [
                    ('company_id', '=', rec.company_id.id),
                    ('status', '=', 'active'),
                    ('rider_type', '=', rec.rider_type),
                ]
                if rec.branch_id:
                    domain.append(('branch_id', '=', rec.branch_id.id))
                else:
                    domain.append(('branch_id', '=', False))
                active_count = self.search_count(domain)
                if active_count > 1:
                    branch_label = f" — فرع {rec.branch_id.name}" if rec.branch_id else ""
                    type_label = dict(rec._fields['rider_type'].selection).get(rec.rider_type, rec.rider_type)
                    raise ValidationError(
                        f'يوجد عقد نشط بالفعل للشركة {rec.company_id.name}{branch_label} '
                        f'من نوع [{type_label}]. يُسمح بعقد واحد نشط لكل نوع مندوبين في نفس الفرع.'
                    )
