import calendar
import math
from datetime import date as date_type
from odoo import models, fields, api
from odoo.exceptions import UserError


class DeliveryDailyPerformance(models.Model):
    _name = 'delivery.daily.performance'
    _description = 'Daily Rider Performance (أداء يومي)'
    _inherit = ['mail.thread']
    _order = 'date desc, rider_id'

    branch_id = fields.Many2one('delivery.company.branch', string='Branch', required=True, tracking=True)
    company_id = fields.Many2one('delivery.company', string='Company', related='branch_id.company_id', store=True)
    rider_id = fields.Many2one('delivery.rider', string='Rider', required=True, tracking=True, ondelete='cascade')
    import_session_id = fields.Many2one('delivery.import.session', string='Import Session')
    date = fields.Date(string='Date', required=True, tracking=True)

    platform_account_id = fields.Char(string='Platform Account ID (معرف الحساب)',
                                       help='Account ID on the platform, may differ from rider if sub-rider')
    account_name = fields.Char(string='Account Name (مستخدم الحساب)')
    vehicle_type_company = fields.Selection([
        ('car', 'Private Car'),
        ('motorcycle', 'Bike'),
    ], string='Vehicle Type (Company)')
    vehicle_type_contract = fields.Selection([
        ('car', 'Car'),
        ('motorcycle', 'Bike'),
    ], string='Vehicle Type (Contract)')
    license_plate = fields.Char(string='License Plate (رقم اللوحة)')

    platform_target = fields.Integer(string='Platform Target (تارجيت)', default=0)
    accepted_orders = fields.Integer(string='Accepted Orders (المهام المقبولة)', default=0)
    delivered_orders = fields.Integer(string='Delivered Orders (المهام المُسلمة)', default=0)
    large_orders_completed = fields.Integer(string='Large Orders Completed (مهام الطلبات الكبيرة)', default=0)
    cancelled_orders = fields.Integer(string='Cancelled Orders (المهام المُلغاة)', default=0)
    rejected_orders = fields.Integer(string='Rejected Orders', default=0)

    valid_online_hours = fields.Float(string='Valid Online Hours', digits=(8, 2), default=0.0)
    peak_hours = fields.Float(string='Peak Hours', digits=(8, 2), default=0.0)
    total_online_hours = fields.Float(string='Total Online Hours', digits=(8, 2), default=0.0)

    is_valid_day = fields.Boolean(string='Valid Day (يوم صالح)', compute='_compute_is_valid_day', store=True)
    validity_notes = fields.Char(string='Validity Notes (سبب الصلاحية)', compute='_compute_is_valid_day', store=True)
    is_must_attend_day = fields.Boolean(string='Must Attend Day', default=False)

    on_time_deliveries = fields.Integer(string='On-Time Deliveries', default=0)
    advance_deliveries = fields.Integer(string='Delivered in Advance', default=0)

    @api.depends('delivered_orders', 'total_online_hours', 'valid_online_hours',
                 'peak_hours', 'accepted_orders', 'branch_id', 'import_session_id')
    def _compute_is_valid_day(self):
        criteria_cache = {}
        for rec in self:
            contract_id = rec.import_session_id.contract_id.id if rec.import_session_id and rec.import_session_id.contract_id else False
            branch_id = rec.branch_id.id if rec.branch_id else False
            cache_key = (contract_id, branch_id)

            if cache_key not in criteria_cache:
                domain = [('is_active', '=', True)]
                if contract_id:
                    criteria = self.env['delivery.validity.criteria'].search(
                        domain + [('contract_id', '=', contract_id)], limit=1)
                else:
                    criteria = False
                if not criteria:
                    criteria = self.env['delivery.validity.criteria'].search(
                        domain + ['|', ('branch_id', '=', branch_id), ('branch_id', '=', False)],
                        limit=1, order='branch_id desc nulls last')
                criteria_cache[cache_key] = criteria
            criteria = criteria_cache[cache_key]

            if not criteria:
                rec.is_valid_day = rec.delivered_orders > 0
                if rec.delivered_orders > 0:
                    rec.validity_notes = '✓ صالح (بدون معايير)'
                else:
                    rec.validity_notes = '✗ لا طلبات مسلمة | لا توجد معايير مضبوطة للفرع'
                continue

            min_hours = criteria.min_daily_online_hours or 0
            min_peak = criteria.min_daily_peak_hours or 0
            # يُفضَّل total_online_hours (مستورد من Excel) على valid_online_hours
            online = rec.total_online_hours if rec.total_online_hours > 0 else rec.valid_online_hours
            peak = rec.peak_hours or 0.0
            delivered = rec.delivered_orders or 0

            reasons = []
            notes = []

            # ── ساعات الاتصال ───────────────────────────────────────────────
            # إذا كانت الساعات = 0 (لم تُستورَد من التقرير اليومي)،
            # نتجاهل شرط الساعات ونعتمد فقط على الطلبات المُسلَّمة.
            if online == 0 and min_hours > 0:
                hours_ok = True  # بيانات الساعات غير متوفرة في هذا التقرير
                notes.append('ساعات غير متوفرة')
            else:
                hours_ok = online >= min_hours if min_hours > 0 else True
                if not hours_ok:
                    reasons.append(f'ساعات {online:.1f}/{min_hours:.0f}h')

            # ── ساعات الذروة ────────────────────────────────────────────────
            if peak == 0 and min_peak > 0:
                peak_ok = True  # بيانات الذروة غير متوفرة
            else:
                peak_ok = peak >= min_peak if min_peak > 0 else True
                if not peak_ok:
                    reasons.append(f'ذروة {peak:.1f}/{min_peak:.0f}h')

            # ── الطلبات المُسلَّمة ───────────────────────────────────────────
            orders_ok = delivered >= 1
            if not orders_ok:
                reasons.append('لا طلبات مسلمة')

            rec.is_valid_day = hours_ok and peak_ok and orders_ok
            if reasons:
                rec.validity_notes = ' | '.join(reasons)
            elif notes:
                rec.validity_notes = '✓ صالح (' + ', '.join(notes) + ')'
            else:
                rec.validity_notes = '✓ صالح'

    def action_recompute_validity(self):
        self._compute_is_valid_day()

    # تم إزالة sql_constraint وتعويضه بـ Python constraint
    # لأن السائقين من نوع الفرىلانسر (sub-riders) المرتبطين بنفس البيرنت
    # يجب أن يُسمح لهم بوجود أكثر من سجل في نفس اليوم والفرع.
    @api.constrains('rider_id', 'date', 'branch_id')
    def _check_unique_rider_date(self):
        for rec in self:
            # السماح بالتكرار إذا كان السائق فرىلانسر (لديه parent_rider_id)
            if rec.rider_id and rec.rider_id.parent_rider_id:
                continue
            duplicate = self.search([
                ('rider_id', '=', rec.rider_id.id),
                ('date', '=', rec.date),
                ('branch_id', '=', rec.branch_id.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                from odoo.exceptions import ValidationError
                raise ValidationError(
                    f'لا يمكن إضافة أكثر من سجل أداء يومي لنفس السائق '
                    f'({rec.rider_id.name}) في نفس اليوم والفرع.\n'
                    f'Only one performance record per rider per day per branch is allowed.'
                )


class DeliveryMonthlyPerformance(models.Model):
    _name = 'delivery.monthly.performance'
    _description = 'Monthly Rider Performance Summary (ملخص أداء شهري)'
    _inherit = ['mail.thread']
    _order = 'period_year desc, period_month desc, rider_id'

    branch_id = fields.Many2one('delivery.company.branch', string='Branch', required=True, tracking=True)
    company_id = fields.Many2one('delivery.company', string='Company', related='branch_id.company_id', store=True)
    rider_id = fields.Many2one('delivery.rider', string='Rider', required=True, tracking=True, ondelete='cascade')
    period_month = fields.Integer(string='Month', required=True)
    period_year = fields.Integer(string='Year', required=True)
    period_display = fields.Char(string='Period', compute='_compute_period_display', store=True)

    is_valid = fields.Boolean(string='Valid DA (صالح)', default=False, tracking=True)
    validity_reason = fields.Char(string='Validity Reason (السبب)', tracking=True)

    valid_days = fields.Integer(string='Valid Contact Days (أيام الاتصال الصالحة)', default=0)
    valid_hours = fields.Float(string='Valid Contact Hours (ساعات الاتصال الصالحة)', digits=(8, 2), default=0.0)
    valid_peak_hours = fields.Float(string='Valid Peak Hours (ساعات الذروة الصالحة)', digits=(8, 2), default=0.0)

    delivered_orders = fields.Integer(string='Delivered Orders (الطلبات المُسلمة)', default=0)
    accepted_orders = fields.Integer(string='Accepted Orders', default=0)
    cancelled_orders = fields.Integer(string='Cancelled Orders', default=0)
    on_time_deliveries = fields.Integer(string='On-Time Deliveries', default=0)
    advance_deliveries = fields.Integer(string='Delivered in Advance', default=0)

    on_time_rate = fields.Float(string='On-Time Delivery Rate', digits=(8, 4), compute='_compute_rates', store=True)
    cancellation_rate = fields.Float(string='Cancellation Rate', digits=(8, 4), compute='_compute_rates', store=True)
    advance_rate = fields.Float(string='Advance Delivery Rate', digits=(8, 4), compute='_compute_rates', store=True)
    experience_score = fields.Float(string='Experience Score', digits=(8, 4), tracking=True)
    performance_level = fields.Selection([
        ('A', 'Level A'),
        ('B', 'Level B'),
        ('C', 'Level C'),
        ('D', 'Level D'),
    ], string='Performance Level', tracking=True)

    order_base_amount = fields.Float(string='Order Base Pricing (التسعير حسب الطلب)', digits=(12, 2), default=0.0)
    capacity_incentive = fields.Float(string='Valid DA Capacity Incentive (حوافز سعة الطلب)', digits=(12, 2), default=0.0)
    experience_incentive = fields.Float(string='Experience Incentive (حوافز التسليم في الوقت)', digits=(12, 2), default=0.0)
    subsidy = fields.Float(string='Subsidy (الإعانة)', digits=(12, 2), default=0.0)
    dxg = fields.Float(string='DXG', digits=(12, 2), default=0.0)
    other_activities = fields.Float(string='Other Activities & Rewards (الأنشطة والمكافآت)', digits=(12, 2), default=0.0)
    deductions = fields.Float(string='Deductions (الخصم)', digits=(12, 2), default=0.0,
                               help='Negative value')
    food_damage_compensation = fields.Float(string='Food Damage Compensation (تعويض تلف الطعام)', digits=(12, 2), default=0.0,
                                              help='Negative value')
    other_adjustment = fields.Float(string='Other Adjustment (تعديل آخر)', digits=(12, 2), default=0.0)
    tips_excl_vat = fields.Float(string='Tips excl. VAT (البقشيش بدون ضريبة)', digits=(12, 2), default=0.0)

    total_revenue = fields.Float(string='Total Revenue', digits=(12, 2),
                                  compute='_compute_total_revenue', store=True)

    @api.depends('period_month', 'period_year')
    def _compute_period_display(self):
        months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        for rec in self:
            rec.period_display = f"{months.get(rec.period_month, '?')} {rec.period_year}"

    @api.depends('delivered_orders', 'on_time_deliveries', 'accepted_orders',
                 'cancelled_orders', 'advance_deliveries')
    def _compute_rates(self):
        for rec in self:
            rec.on_time_rate = (rec.on_time_deliveries / rec.delivered_orders) if rec.delivered_orders else 0
            rec.cancellation_rate = (rec.cancelled_orders / rec.accepted_orders) if rec.accepted_orders else 0
            rec.advance_rate = (rec.advance_deliveries / rec.delivered_orders) if rec.delivered_orders else 0

    @api.depends('order_base_amount', 'capacity_incentive', 'experience_incentive',
                 'subsidy', 'dxg', 'other_activities', 'deductions',
                 'food_damage_compensation', 'other_adjustment', 'tips_excl_vat')
    def _compute_total_revenue(self):
        for rec in self:
            rec.total_revenue = (
                rec.order_base_amount + rec.capacity_incentive + rec.experience_incentive +
                rec.subsidy + rec.dxg + rec.other_activities +
                rec.deductions + rec.food_damage_compensation + rec.other_adjustment +
                rec.tips_excl_vat
            )

    # تم إزالة sql_constraint وتعويضه بـ Python constraint
    # لأن السائقين من نوع الفرىلانسر (sub-riders) المرتبطين بنفس البيرنت
    # يجب أن يُسمح لهم بوجود أكثر من سجل في نفس الشهر والفرع.
    @api.constrains('rider_id', 'period_month', 'period_year', 'branch_id')
    def _check_unique_rider_month(self):
        for rec in self:
            # السماح بالتكرار إذا كان السائق فرىلانسر (لديه parent_rider_id)
            if rec.rider_id and rec.rider_id.parent_rider_id:
                continue
            duplicate = self.search([
                ('rider_id', '=', rec.rider_id.id),
                ('period_month', '=', rec.period_month),
                ('period_year', '=', rec.period_year),
                ('branch_id', '=', rec.branch_id.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                from odoo.exceptions import ValidationError
                raise ValidationError(
                    f'لا يمكن إضافة أكثر من سجل أداء شهري لنفس السائق '
                    f'({rec.rider_id.name}) في نفس الشهر والفرع.\n'
                    f'Only one monthly performance record per rider per month per branch.'
                )

    # ──────────────────────────────────────────────────────────────────────
    # Validity Computation from Daily Records
    # حساب الصلاحية الشهرية من السجلات اليومية
    # ──────────────────────────────────────────────────────────────────────

    def action_compute_from_daily(self):
        """Button action: aggregate daily records then compute monthly validity."""
        if not self:
            raise UserError('يرجى تحديد سجل واحد على الأقل.')
        count = 0
        for rec in self:
            rec._aggregate_from_daily_records()
            count += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تم الحساب',
                'message': f'تمت معالجة {count} سجل بنجاح',
                'type': 'success',
                'sticky': False,
            },
        }

    def _aggregate_from_daily_records(self):
        """
        Pull all daily performance records for this rider/branch/month,
        aggregate numeric fields, then apply validity criteria.
        """
        self.ensure_one()
        year = self.period_year
        month = self.period_month
        days_in_month = calendar.monthrange(year, month)[1]
        d_start = date_type(year, month, 1)
        d_end = date_type(year, month, days_in_month)

        Daily = self.env['delivery.daily.performance']
        daily_recs = Daily.search([
            ('rider_id', '=', self.rider_id.id),
            ('branch_id', '=', self.branch_id.id),
            ('date', '>=', d_start),
            ('date', '<=', d_end),
        ])

        if not daily_recs:
            # لا توجد سجلات يومية — إذا كان valid_days محدداً مسبقاً (من استيراد شهري)
            # نحسب الصلاحية من القيمة المخزّنة بدلاً من تصفيرها.
            stored_valid_days = self.valid_days or 0
            if stored_valid_days > 0:
                criteria = self._get_active_validity_criteria()
                is_valid, reason = self._check_monthly_validity(
                    stored_valid_days, days_in_month, criteria)
                self.write({
                    'is_valid': is_valid,
                    'validity_reason': reason or '',
                })
            else:
                self.write({
                    'validity_reason': 'لا توجد سجلات يومية لهذا الشهر / No daily records',
                    'is_valid': False,
                    'valid_days': 0,
                })
            return

        valid_recs = daily_recs.filtered(lambda d: d.is_valid_day)

        valid_days = len(valid_recs)
        valid_hours = sum(
            d.valid_online_hours or d.total_online_hours or 0.0
            for d in valid_recs
        )
        valid_peak_hours = sum(d.peak_hours or 0.0 for d in valid_recs)
        delivered_orders = sum(d.delivered_orders or 0 for d in daily_recs)
        accepted_orders = sum(d.accepted_orders or 0 for d in daily_recs)
        cancelled_orders = sum(d.cancelled_orders or 0 for d in daily_recs)
        on_time_deliveries = sum(d.on_time_deliveries or 0 for d in daily_recs)
        advance_deliveries = sum(d.advance_deliveries or 0 for d in daily_recs)

        criteria = self._get_active_validity_criteria()
        is_valid, reason = self._check_monthly_validity(valid_days, days_in_month, criteria)

        self.write({
            'valid_days': valid_days,
            'valid_hours': valid_hours,
            'valid_peak_hours': valid_peak_hours,
            'delivered_orders': delivered_orders,
            'accepted_orders': accepted_orders,
            'cancelled_orders': cancelled_orders,
            'on_time_deliveries': on_time_deliveries,
            'advance_deliveries': advance_deliveries,
            'is_valid': is_valid,
            'validity_reason': reason,
        })

    def _get_active_validity_criteria(self):
        """
        Find the most specific validity criteria for this monthly record.
        Priority: contract + branch → contract only → branch → global first.
        """
        self.ensure_one()
        VC = self.env['delivery.validity.criteria']
        domain_active = [('is_active', '=', True)]

        contract = self.env['delivery.contract'].search([
            ('company_id', '=', self.company_id.id),
            ('status', '=', 'active'),
            '|',
            ('branch_id', '=', self.branch_id.id),
            ('branch_id', '=', False),
        ], order='branch_id desc nulls last', limit=1)

        if contract:
            criteria = VC.search(domain_active + [('contract_id', '=', contract.id)], limit=1)
            if criteria:
                return criteria

        criteria = VC.search(
            domain_active + ['|', ('branch_id', '=', self.branch_id.id), ('branch_id', '=', False)],
            order='branch_id desc nulls last', limit=1,
        )
        return criteria

    def _check_monthly_validity(self, valid_days, days_in_month, criteria):
        """
        Apply validity criteria and return (is_valid: bool, reason: str).

        Rules applied (in order):
        1. Mid-month join: if rider joined this month, require
           ceil(remaining_days × pct/100) valid days instead of min_valid_days.
        2. Otherwise: valid_days >= min_valid_days.
        """
        if not criteria:
            if valid_days > 0:
                return True, ''
            return False, 'لا توجد معايير صلاحية مرتبطة بالعقد'

        min_valid_days = criteria.min_valid_days or 26
        reasons = []

        rider_join = (
            self.rider_id.join_date
            or self.rider_id.work_start_date
        )
        year = self.period_year
        month = self.period_month

        if (rider_join
                and rider_join.year == year
                and rider_join.month == month
                and rider_join.day > 1):
            remaining_days = days_in_month - rider_join.day + 1
            mid_pct = (criteria.min_calendar_pct_mid_month or 85.0) / 100.0
            required_days = math.ceil(remaining_days * mid_pct)
            if valid_days < required_days:
                reasons.append(
                    f'انضم {rider_join.strftime("%d/%m")}: '
                    f'مطلوب {required_days} يوم صالح من {remaining_days} متاحة '
                    f'({criteria.min_calendar_pct_mid_month:.0f}%) — حقق {valid_days}'
                )
        else:
            if valid_days < min_valid_days:
                reasons.append(
                    f'أيام صالحة {valid_days}/{min_valid_days} '
                    f'(الحد الأدنى المطلوب)'
                )

        is_valid = len(reasons) == 0
        return is_valid, ' | '.join(reasons) if reasons else ''
