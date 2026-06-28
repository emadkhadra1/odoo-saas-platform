from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DeliverySettlement(models.Model):
    _name = 'delivery.settlement'
    _description = 'Delivery Settlement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    company_id = fields.Many2one('delivery.company', string='Company', required=True, tracking=True, ondelete='cascade')
    branch_id = fields.Many2one('delivery.company.branch', string='Branch', tracking=True,
                                 domain="[('company_id', '=', company_id)]")
    contract_id = fields.Many2one('delivery.contract', string='Contract', tracking=True,
                                  domain="[('company_id', '=', company_id), ('status', '=', 'active'), '|', ('branch_id', '=', branch_id), ('branch_id', '=', False)]")
    settlement_number = fields.Char(string='Settlement Number', required=True, tracking=True)
    period_start = fields.Date(string='Period Start', required=True)
    period_end = fields.Date(string='Period End', required=True)
    cycle = fields.Selection([
        ('weekly', 'Weekly'),
        ('semi_monthly', 'Semi-Monthly'),
        ('monthly', 'Monthly'),
    ], string='Settlement Cycle', default='monthly', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ], string='Status', default='draft', required=True, tracking=True)
    total_orders = fields.Integer(string='Total Orders', default=0)
    gross_amount = fields.Float(string='Gross Amount', digits=(12, 2), default=0.0, tracking=True)

    order_base_total = fields.Float(string='Order Base Total', digits=(12, 2), default=0.0)
    capacity_incentive_total = fields.Float(string='Capacity Incentive Total', digits=(12, 2), default=0.0)
    experience_incentive_total = fields.Float(string='Experience Incentive Total', digits=(12, 2), default=0.0)
    subsidy_total = fields.Float(string='Subsidy Total', digits=(12, 2), default=0.0)
    dxg_total = fields.Float(string='DXG Total', digits=(12, 2), default=0.0)
    tips_total = fields.Float(string='Tips Total (excl. VAT)', digits=(12, 2), default=0.0)
    vehicle_rental_total = fields.Float(
        string='Vehicle Rental Deductions Total (إجمالي اقتطاعات إيجار المركبات)',
        digits=(12, 2), default=0.0,
    )
    subcontract_fee_total = fields.Float(
        string='Subcontract Management Fees Total (إجمالي رسوم إدارة المقاولين)',
        digits=(12, 2), default=0.0,
    )
    provider_fee_total = fields.Float(
        string='إجمالي خصم مزود الخدمة (Service Provider Fees Total)',
        digits=(12, 2), default=0.0,
        help='مجموع المبالغ الشهرية المستقطعة لصالح شركات مزودة الخدمة لجميع المناديب الفرى لانسر '
             '(تناسبياً حسب تاريخ استلام الـ ID).',
    )
    monthly_deduction_total = fields.Float(
        string='إجمالي الاستقطاعات الشهرية (Monthly Deductions Total)',
        digits=(12, 2), default=0.0,
        help='مجموع الاستقطاعات الشهرية (إيجار، سكن، بنزين، قسط...) من سجلات delivery.rider.deduction',
    )
    advance_deduction_total = fields.Float(
        string='إجمالي السلف المستردة (Advance Deductions Total)',
        digits=(12, 2), default=0.0,
        help='مجموع مبالغ السلفة المستقطعة من مستحقات المناديب هذا الشهر',
    )

    penalties = fields.Float(string='Penalties', digits=(12, 2), default=0.0)
    bonuses = fields.Float(string='Bonuses', digits=(12, 2), default=0.0)
    adjustments = fields.Float(string='Adjustments', digits=(12, 2), default=0.0)
    vat_amount = fields.Float(string='VAT Amount (مبلغ الضريبة)', digits=(12, 2), default=0.0)
    net_amount = fields.Float(string='Net Amount', digits=(12, 2), default=0.0,
                              compute='_compute_net_amount', store=True, tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approved_at = fields.Datetime(string='Approved At')
    notes = fields.Text(string='Notes')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    valid_rider_count = fields.Integer(string='Valid Riders (صالح)', default=0)
    invalid_rider_count = fields.Integer(string='Invalid Riders (غير صالح)', default=0)

    item_ids = fields.One2many('delivery.settlement.item', 'settlement_id', string='Settlement Items')
    item_count = fields.Integer(compute='_compute_item_count')

    # ── Payslip Integration ──────────────────────────────────────────────────
    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        string='Payslip Batch (دفعة كشوف الرواتب)',
        readonly=True,
        copy=False,
        tracking=True,
        help='Payslip batch generated from this settlement for riders linked to HR employees.',
    )
    payslip_count = fields.Integer(
        string='# Payslips',
        compute='_compute_payslip_count',
    )

    @api.depends('gross_amount', 'penalties', 'bonuses', 'adjustments', 'vat_amount',
                 'vehicle_rental_total', 'subcontract_fee_total', 'provider_fee_total',
                 'monthly_deduction_total', 'advance_deduction_total')
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = (
                rec.gross_amount
                - rec.penalties
                + rec.bonuses
                + rec.adjustments
                - rec.vat_amount
                - rec.vehicle_rental_total
                - rec.subcontract_fee_total
                - rec.provider_fee_total
                - rec.monthly_deduction_total
                - rec.advance_deduction_total
            )

    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)

    def _compute_payslip_count(self):
        for rec in self:
            if rec.payslip_run_id:
                rec.payslip_count = self.env['hr.payslip'].search_count([
                    ('payslip_run_id', '=', rec.payslip_run_id.id)
                ])
            else:
                rec.payslip_count = 0

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.branch_id = False
            active_contract = self.env['delivery.contract'].search([
                ('company_id', '=', self.company_id.id),
                ('status', '=', 'active'),
            ], limit=1)
            if active_contract:
                self.contract_id = active_contract.id
                self.cycle = active_contract.settlement_cycle

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            active_contract = self.env['delivery.contract'].search([
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', self.branch_id.id),
                ('status', '=', 'active'),
            ], limit=1)
            if active_contract:
                self.contract_id = active_contract.id
                self.cycle = active_contract.settlement_cycle

    def _match_vehicle(self, rule, rider_vehicle):
        if not rule.vehicle_type or rule.vehicle_type == 'all':
            return True
        return rule.vehicle_type == rider_vehicle

    def _calc_tiered(self, slab_rules, orders, rider_vehicle):
        for rule in slab_rules:
            if not self._match_vehicle(rule, rider_vehicle):
                continue
            remaining = orders
            total = 0.0
            for slab in rule.slab_ids.sorted('from_orders'):
                if remaining <= 0:
                    break
                slab_max = (slab.to_orders - slab.from_orders + 1) if slab.to_orders else remaining
                qty = min(remaining, slab_max)
                amt = qty * slab.price_per_order
                if slab.max_payout and amt > slab.max_payout:
                    amt = slab.max_payout
                total += amt
                remaining -= qty
            return total
        return 0.0

    def _calc_per_order(self, per_order_rules, orders, rider_vehicle):
        for rule in per_order_rules:
            if not self._match_vehicle(rule, rider_vehicle):
                continue
            return orders * rule.base_amount
        return 0.0

    def _calc_fixed_salary(self, fixed_rules, mp, rider_vehicle):
        for rule in fixed_rules:
            if not self._match_vehicle(rule, rider_vehicle):
                continue
            salary = rule.monthly_total or (rule.daily_rate * (rule.working_days or 30))
            valid_days = mp.valid_days or 0
            working_days = rule.working_days or 26
            if valid_days < working_days:
                salary = rule.daily_rate * valid_days
            orders = mp.delivered_orders or 0
            bonus = 0.0
            if rule.bonus_threshold and rule.bonus_per_order and working_days:
                avg_daily = orders / max(valid_days, 1)
                if avg_daily > rule.bonus_threshold:
                    extra_per_day = avg_daily - rule.bonus_threshold
                    bonus = extra_per_day * valid_days * rule.bonus_per_order
            return salary + bonus
        return 0.0

    def _calc_per_distance(self, per_km_rules, mp, rider_vehicle):
        for rule in per_km_rules:
            if not self._match_vehicle(rule, rider_vehicle):
                continue
            orders = mp.delivered_orders or 0
            return orders * rule.base_amount
        return 0.0

    def _calc_subcontract_fee(self, subcontract_fee_rules, gross_amount, order_base, rider_vehicle):
        for rule in subcontract_fee_rules:
            if not self._match_vehicle(rule, rider_vehicle):
                continue
            basis = rule.subcontract_fee_basis or 'gross'
            if basis == 'flat':
                return rule.base_amount
            elif basis == 'order_base':
                return (order_base * rule.subcontract_fee_pct / 100.0) if rule.subcontract_fee_pct else rule.base_amount
            else:
                return (gross_amount * rule.subcontract_fee_pct / 100.0) if rule.subcontract_fee_pct else rule.base_amount
        return 0.0

    def _get_rider_extra_deductions(self, rider, period_month, period_year):
        """جلب الاستقطاعات الشهرية والسلفة للمندوب لفترة التسوية.

        Returns: (monthly_deduction, advance_deduction)
        - monthly_deduction : مجموع delivery.rider.deduction للشهر (إيجار، سكن، قسط، سلف...)
        - advance_deduction : مبلغ السلفة المقدمة من المندوب (advance_amount) إذا advance_paid
        """
        # ── الاستقطاعات الشهرية من نموذج delivery.rider.deduction ──────────
        deduction_recs = self.env['delivery.rider.deduction'].search([
            ('rider_id', '=', rider.id),
            ('month', '=', period_month),
            ('year', '=', period_year),
        ])
        monthly_deduction = sum(d.total_deduction for d in deduction_recs)

        # ── السلفة المقدمة من المندوب ─────────────────────────────────────
        advance_deduction = 0.0
        if rider.advance_paid and (rider.advance_amount or 0.0) > 0:
            advance_deduction = rider.advance_amount

        return monthly_deduction, advance_deduction

    def _get_provider_fee(self, rider, period_month, period_year):
        """خصم مزود الخدمة الشهري لكل مندوب فرى لانسر.

        - يُحتسب فقط إذا كان للمندوب شركة مزودة خدمة بمبلغ شهري > 0.
        - يُخصم المبلغ من الفاتورة المحتسبة، والباقي يذهب للمندوب.
        - إذا استلم المندوب الـ ID خلال شهر التسوية (id_receipt_date) يُحتسب
          الخصم تناسبياً بالأيام:
              المبلغ × (الأيام من تاريخ الاستلام لآخر الشهر ÷ عدد أيام الشهر)
        - إذا استلم الـ ID قبل بداية الشهر (أو لا يوجد تاريخ) → المبلغ كامل.
        """
        import calendar
        provider = rider.service_provider_id
        if not provider or (provider.monthly_fee_per_rider or 0.0) <= 0:
            return 0.0

        monthly_fee = provider.monthly_fee_per_rider
        days_in_month = calendar.monthrange(period_year, period_month)[1]

        receipt = rider.id_receipt_date
        if receipt and receipt.year == period_year and receipt.month == period_month:
            active_days = days_in_month - receipt.day + 1
            if active_days < 0:
                active_days = 0
            return round(monthly_fee * active_days / days_in_month, 2)

        # تاريخ الاستلام بعد فترة التسوية → لم يكن قد استلم بعد، لا خصم
        if receipt and (receipt.year, receipt.month) > (period_year, period_month):
            return 0.0

        # استلم قبل الشهر أو لا يوجد تاريخ → المبلغ كامل
        return monthly_fee

    def _get_monthly_target(self, month, year):
        self.ensure_one()
        target_model = self.env['delivery.company.target']
        domain_base = [('month', '=', month), ('year', '=', year), ('company_id', '=', self.company_id.id)]
        if self.branch_id:
            target = target_model.search(domain_base + [('branch_id', '=', self.branch_id.id)], limit=1,
                                          order='write_date desc')
            if target:
                return target
        return target_model.search(domain_base + [('branch_id', '=', False)], limit=1,
                                    order='write_date desc')

    def _calc_cap_incentive_from_target(self, target, valid_das, rider_vehicle):
        if not target:
            return 0.0
        if valid_das >= target.level_a_min_valid_das:
            return target.level_a_bike_amount if rider_vehicle == 'motorcycle' else target.level_a_car_amount
        elif valid_das >= target.level_b_min_valid_das:
            return target.level_b_bike_amount if rider_vehicle == 'motorcycle' else target.level_b_car_amount
        elif valid_das >= target.level_c_min_valid_das:
            return target.level_c_bike_amount if rider_vehicle == 'motorcycle' else target.level_c_car_amount
        return 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # حساب التسوية — يتفرع حسب نمط التسعير في العقد
    # ─────────────────────────────────────────────────────────────────────────

    def action_compute_settlement(self):
        self.ensure_one()
        if self.status != 'draft':
            raise ValidationError('يمكن حساب التسوية فقط في حالة المسودة / Only draft settlements can be computed.')
        if not self.branch_id:
            raise ValidationError('يجب اختيار الفرع أولاً / Please select a branch first.')
        if not self.contract_id:
            raise ValidationError('يجب اختيار العقد أولاً / Please select a contract first.')

        self.item_ids.unlink()

        period_month = self.period_start.month
        period_year = self.period_start.year
        monthly_records = self.env['delivery.monthly.performance'].search([
            ('branch_id', '=', self.branch_id.id),
            ('period_month', '=', period_month),
            ('period_year', '=', period_year),
        ])
        if not monthly_records:
            raise ValidationError(
                f'لا توجد بيانات أداء شهري للفرع {self.branch_id.name} لشهر {period_month}/{period_year}\n'
                f'No monthly performance data found for branch {self.branch_id.name} for {period_month}/{period_year}'
            )

        pricing_mode = self.contract_id.pricing_mode or 'standard'

        if pricing_mode == 'keeta':
            return self._compute_keeta(monthly_records)
        elif pricing_mode == 'hungerstation_internal':
            return self._compute_hungerstation_internal(monthly_records)
        elif pricing_mode == 'tier_per_order':
            return self._compute_tier_per_order(monthly_records)
        elif pricing_mode == 'fixed_fee':
            return self._compute_fixed_fee(monthly_records)
        else:
            return self._compute_standard(monthly_records)

    # ── نمط كيتا — 4 حالات ───────────────────────────────────────────────────

    def _compute_keeta(self, monthly_records):
        """
        نمط كيتا: 4 حالات بناءً على (صالح / غير صالح) × (حقق التارجيت / لم يحقق)

        الحالة 1 — صالح + حقق التارجيت (360 طلب):
            أساسي 1500 + طلبات إضافية (361-400 بـ 8 ريال، 400+ بـ 10 ريال)
            + بونص تارجيت الشركة (37.5% من bонص الشركة ÷ عدد المناديب المؤهلين)
            + تعديل شريحة الأداء (A=+100, B=-300, C=-500, D=-1000)
        الحالة 2 — صالح + لم يحقق التارجيت:
            عدد الطلبات × 4 ريال
        الحالة 3 — غير صالح + حقق التارجيت:
            عدد الطلبات × 4 ريال
        الحالة 4 — غير صالح + لم يحقق التارجيت:
            عدد الطلبات × 2 ريال
        """
        self.ensure_one()
        contract = self.contract_id
        item_model = self.env['delivery.settlement.item']

        target_orders = contract.keeta_target_orders or 360
        base_salary = contract.keeta_base_salary or 1500.0
        extra_threshold = contract.keeta_extra_threshold or 400
        rate_extra_1 = contract.keeta_rate_extra_1 or 8.0
        rate_extra_2 = contract.keeta_rate_extra_2 or 10.0
        company_bonus_pct = (contract.keeta_company_bonus_pct or 37.5) / 100.0
        tier_a_bonus = contract.keeta_tier_a_bonus or 100.0
        tier_b_penalty = contract.keeta_tier_b_penalty or 300.0
        tier_c_penalty = contract.keeta_tier_c_penalty or 500.0
        tier_d_penalty = contract.keeta_tier_d_penalty or 1000.0
        valid_no_target_rate = contract.keeta_valid_no_target_rate or 4.0
        invalid_target_rate = contract.keeta_invalid_target_rate or 4.0
        invalid_no_target_rate = contract.keeta_invalid_no_target_rate or 2.0

        period_month = self.period_start.month
        period_year = self.period_start.year
        monthly_target = self._get_monthly_target(period_month, period_year)

        # تحديد المناديب المؤهلين للبونص الشركة (صالح + حقق التارجيت)
        eligible_for_bonus = [
            mp for mp in monthly_records
            if getattr(mp, 'is_valid', False) and (mp.delivered_orders or 0) >= target_orders
        ]
        eligible_count = len(eligible_for_bonus)

        # حساب بونص الشركة للمندوب
        company_bonus_per_rider = 0.0
        if monthly_target and eligible_count > 0:
            company_total_bonus = getattr(monthly_target, 'tga_excl_vat', 0.0) or 0.0
            if company_total_bonus > 0:
                company_bonus_per_rider = (company_total_bonus * company_bonus_pct) / eligible_count

        total_orders = total_gross = total_order_base = 0.0
        total_vehicle_rental = 0.0
        total_monthly_deduction = total_advance_deduction = 0.0
        total_provider_fee = 0.0
        total_tier_bonuses = total_tier_penalties = 0.0
        valid_count = invalid_count = 0
        period_month = self.period_start.month
        period_year = self.period_start.year

        for mp in monthly_records:
            rider = mp.rider_id
            orders = mp.delivered_orders or 0
            is_valid = getattr(mp, 'is_valid', False)
            achieved_target = orders >= target_orders

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            order_base = 0.0
            tier_adjustment = 0.0
            bonus_amount = 0.0
            case_label = ''

            if is_valid and achieved_target:
                case_label = 'صالح + تارجيت'
                order_base = base_salary
                orders_above = orders - target_orders
                if orders_above > 0:
                    orders_in_range_1 = min(orders_above, extra_threshold - target_orders)
                    orders_in_range_2 = max(0, orders_above - (extra_threshold - target_orders))
                    order_base += (orders_in_range_1 * rate_extra_1) + (orders_in_range_2 * rate_extra_2)
                bonus_amount = company_bonus_per_rider
                level = rider.performance_level
                if level == 'A':
                    tier_adjustment = tier_a_bonus
                elif level == 'B':
                    tier_adjustment = -tier_b_penalty
                elif level == 'C':
                    tier_adjustment = -tier_c_penalty
                elif level == 'D':
                    tier_adjustment = -tier_d_penalty

            elif is_valid and not achieved_target:
                case_label = 'صالح + بدون تارجيت'
                order_base = orders * valid_no_target_rate

            elif not is_valid and achieved_target:
                case_label = 'غير صالح + تارجيت'
                order_base = orders * invalid_target_rate

            else:
                case_label = 'غير صالح + بدون تارجيت'
                order_base = orders * invalid_no_target_rate

            vehicle_rental_deduction = 0.0
            if rider.vehicle_ownership == 'rented_from_company' and rider.vehicle_rental_amount > 0:
                vehicle_rental_deduction = rider.vehicle_rental_amount

            monthly_deduction, advance_deduction = self._get_rider_extra_deductions(
                rider, period_month, period_year)
            provider_fee = self._get_provider_fee(rider, period_month, period_year)

            gross = order_base + bonus_amount + tier_adjustment - vehicle_rental_deduction

            rider_bonus = bonus_amount + max(0.0, tier_adjustment)
            rider_penalty = abs(min(0.0, tier_adjustment))
            if tier_adjustment < 0:
                total_tier_penalties += abs(tier_adjustment)
            else:
                total_tier_bonuses += tier_adjustment

            item_model.create({
                'settlement_id': self.id,
                'rider_id': rider.id,
                'is_valid_da': is_valid,
                'validity_reason': case_label,
                'orders': orders,
                'order_base_amount': order_base,
                'capacity_incentive': 0.0,
                'experience_incentive': 0.0,
                'subsidy': 0.0,
                'dxg': 0.0,
                'tips_excl_vat': 0.0,
                'other_activities': bonus_amount,
                'food_damage': 0.0,
                'penalties': rider_penalty,
                'bonuses': rider_bonus,
                'adjustments': 0.0,
                'gross_amount': gross,
                'vehicle_rental_deduction': vehicle_rental_deduction,
                'subcontract_mgmt_fee': 0.0,
                'provider_fee_deduction': provider_fee,
                'monthly_deduction': monthly_deduction,
                'advance_deduction': advance_deduction,
            })

            total_orders += orders
            total_gross += gross
            total_order_base += order_base
            total_vehicle_rental += vehicle_rental_deduction
            total_monthly_deduction += monthly_deduction
            total_provider_fee += provider_fee
            total_advance_deduction += advance_deduction

        notes_line = (
            f'نمط: كيتا | تارجيت: {target_orders} | '
            f'مناديب مؤهلون للبونص: {eligible_count} | '
            f'بونص الشركة/مندوب: {company_bonus_per_rider:.2f} ريال'
        )

        self.write({
            'total_orders': int(total_orders),
            'gross_amount': total_gross,
            'order_base_total': total_order_base,
            'capacity_incentive_total': 0.0,
            'experience_incentive_total': 0.0,
            'subsidy_total': 0.0,
            'dxg_total': 0.0,
            'tips_total': 0.0,
            'penalties': total_tier_penalties,
            'bonuses': total_tier_bonuses,
            'vehicle_rental_total': total_vehicle_rental,
            'subcontract_fee_total': 0.0,
            'provider_fee_total': total_provider_fee,
            'monthly_deduction_total': total_monthly_deduction,
            'advance_deduction_total': total_advance_deduction,
            'valid_rider_count': valid_count,
            'invalid_rider_count': invalid_count,
            'notes': (self.notes or '') + '\n' + notes_line if self.notes else notes_line,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ── نمط كفالة هنقر ───────────────────────────────────────────────────────

    def _compute_hungerstation_internal(self, monthly_records):
        """
        نمط كفالة هنقرستيشين:
        - إذا حقق المندوب التارجيت (550 طلب):
            أساسي 1500 + (الطلبات فوق 550 × 8 ريال/طلب)
        - إذا لم يحقق التارجيت:
            عدد الطلبات × 4 ريال
        """
        self.ensure_one()
        contract = self.contract_id
        item_model = self.env['delivery.settlement.item']

        target_orders = contract.hs_target_orders or 550
        base_salary = contract.hs_base_salary or 1500.0
        rate_above = contract.hs_rate_above_target or 8.0
        rate_below = contract.hs_rate_below_target or 4.0

        total_orders = total_gross = total_order_base = 0.0
        total_vehicle_rental = 0.0
        total_monthly_deduction = total_advance_deduction = 0.0
        total_provider_fee = 0.0
        valid_count = invalid_count = 0
        period_month = self.period_start.month
        period_year = self.period_start.year

        for mp in monthly_records:
            rider = mp.rider_id
            orders = mp.delivered_orders or 0
            is_valid = getattr(mp, 'is_valid', False)
            achieved_target = orders >= target_orders

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            if achieved_target:
                extra_orders = orders - target_orders
                order_base = base_salary + (extra_orders * rate_above)
                case_label = f'تارجيت محقق ({orders} طلب)'
            else:
                order_base = orders * rate_below
                case_label = f'بدون تارجيت ({orders} طلب)'

            vehicle_rental_deduction = 0.0
            if rider.vehicle_ownership == 'rented_from_company' and rider.vehicle_rental_amount > 0:
                vehicle_rental_deduction = rider.vehicle_rental_amount

            monthly_deduction, advance_deduction = self._get_rider_extra_deductions(
                rider, period_month, period_year)
            provider_fee = self._get_provider_fee(rider, period_month, period_year)

            gross = order_base - vehicle_rental_deduction

            item_model.create({
                'settlement_id': self.id,
                'rider_id': rider.id,
                'is_valid_da': is_valid,
                'validity_reason': case_label,
                'orders': orders,
                'order_base_amount': order_base,
                'capacity_incentive': 0.0,
                'experience_incentive': 0.0,
                'subsidy': 0.0,
                'dxg': 0.0,
                'tips_excl_vat': 0.0,
                'other_activities': 0.0,
                'food_damage': 0.0,
                'penalties': 0.0,
                'bonuses': 0.0,
                'adjustments': 0.0,
                'gross_amount': gross,
                'vehicle_rental_deduction': vehicle_rental_deduction,
                'subcontract_mgmt_fee': 0.0,
                'provider_fee_deduction': provider_fee,
                'monthly_deduction': monthly_deduction,
                'advance_deduction': advance_deduction,
            })

            total_orders += orders
            total_gross += gross
            total_order_base += order_base
            total_vehicle_rental += vehicle_rental_deduction
            total_monthly_deduction += monthly_deduction
            total_provider_fee += provider_fee
            total_advance_deduction += advance_deduction

        notes_line = (
            f'نمط: كفالة هنقر | تارجيت: {target_orders} | '
            f'أساسي: {base_salary} ريال | '
            f'إضافي فوق التارجيت: {rate_above} ريال/طلب'
        )

        self.write({
            'total_orders': int(total_orders),
            'gross_amount': total_gross,
            'order_base_total': total_order_base,
            'capacity_incentive_total': 0.0,
            'experience_incentive_total': 0.0,
            'subsidy_total': 0.0,
            'dxg_total': 0.0,
            'tips_total': 0.0,
            'penalties': 0.0,
            'vehicle_rental_total': total_vehicle_rental,
            'subcontract_fee_total': 0.0,
            'provider_fee_total': total_provider_fee,
            'monthly_deduction_total': total_monthly_deduction,
            'advance_deduction_total': total_advance_deduction,
            'valid_rider_count': valid_count,
            'invalid_rider_count': invalid_count,
            'notes': (self.notes or '') + '\n' + notes_line if self.notes else notes_line,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ── نمط الشرائح لكل طلب (النمط القديم - backward compatible) ─────────────

    def _compute_tier_per_order(self, monthly_records):
        """
        النمط القديم: شرائح بناءً على عدد المناديب الصالحين.
        يحتسب سعر الطلب حسب الشريحة المحققة × عدد الطلبات لكل مندوب صالح.
        """
        self.ensure_one()
        contract = self.contract_id
        item_model = self.env['delivery.settlement.item']

        if not contract.tier_ids:
            raise ValidationError(
                'العقد من نمط "شرائح لكل طلب" لكن لا توجد شرائح محددة!\n'
                'اذهب إلى العقد وأضف الشرائح في تبويب "شرائح التسعير".\n\n'
                'Contract is in "Tier Per Order" mode but has no tiers defined!\n'
                'Go to the contract and add tiers in the "Pricing Tiers" tab.'
            )

        valid_das_count = sum(1 for mp in monthly_records if getattr(mp, 'is_valid', False))

        matched_tier = None
        for tier in contract.tier_ids.sorted('sequence'):
            if tier.matches(valid_das_count):
                matched_tier = tier
                break

        total_orders = total_gross = total_order_base = 0.0
        total_vehicle_rental = total_subcontract_fees = 0.0
        total_monthly_deduction = total_advance_deduction = 0.0
        total_provider_fee = 0.0
        valid_count = invalid_count = 0
        period_month = self.period_start.month
        period_year = self.period_start.year

        for mp in monthly_records:
            rider = mp.rider_id
            orders = mp.delivered_orders or 0
            rider_vehicle = rider.vehicle_type or 'motorcycle'
            is_valid = getattr(mp, 'is_valid', False)

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            order_base = 0.0
            if is_valid and matched_tier:
                if rider_vehicle == 'car':
                    order_base = matched_tier.price_per_order_car * orders
                else:
                    order_base = matched_tier.price_per_order_bike * orders

            vehicle_rental_deduction = 0.0
            if rider.vehicle_ownership == 'rented_from_company' and rider.vehicle_rental_amount > 0:
                vehicle_rental_deduction = rider.vehicle_rental_amount

            monthly_deduction, advance_deduction = self._get_rider_extra_deductions(
                rider, period_month, period_year)
            provider_fee = self._get_provider_fee(rider, period_month, period_year)

            gross = order_base - vehicle_rental_deduction

            item_model.create({
                'settlement_id': self.id,
                'rider_id': rider.id,
                'is_valid_da': is_valid,
                'orders': orders,
                'order_base_amount': order_base,
                'capacity_incentive': 0.0,
                'experience_incentive': 0.0,
                'subsidy': 0.0,
                'dxg': 0.0,
                'tips_excl_vat': 0.0,
                'other_activities': 0.0,
                'food_damage': 0.0,
                'penalties': 0.0,
                'bonuses': 0.0,
                'adjustments': 0.0,
                'gross_amount': gross,
                'vehicle_rental_deduction': vehicle_rental_deduction,
                'subcontract_mgmt_fee': 0.0,
                'provider_fee_deduction': provider_fee,
                'monthly_deduction': monthly_deduction,
                'advance_deduction': advance_deduction,
            })

            total_orders += orders
            total_gross += gross
            total_order_base += order_base
            total_vehicle_rental += vehicle_rental_deduction
            total_monthly_deduction += monthly_deduction
            total_provider_fee += provider_fee
            total_advance_deduction += advance_deduction

        tier_label = matched_tier.name if matched_tier else 'لا توجد شريحة مطابقة'
        notes_line = (
            f'نمط: شرائح لكل طلب | الشريحة المحققة: {tier_label} '
            f'({valid_das_count} مندوب صالح)'
        )

        self.write({
            'total_orders': int(total_orders),
            'gross_amount': total_gross,
            'order_base_total': total_order_base,
            'capacity_incentive_total': 0.0,
            'experience_incentive_total': 0.0,
            'subsidy_total': 0.0,
            'dxg_total': 0.0,
            'tips_total': 0.0,
            'penalties': 0.0,
            'vehicle_rental_total': total_vehicle_rental,
            'subcontract_fee_total': 0.0,
            'provider_fee_total': total_provider_fee,
            'monthly_deduction_total': total_monthly_deduction,
            'advance_deduction_total': total_advance_deduction,
            'valid_rider_count': valid_count,
            'invalid_rider_count': invalid_count,
            'notes': (self.notes or '') + '\n' + notes_line if self.notes else notes_line,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ── نمط الرسوم الشهرية الثابتة (هنقر فرى / جاهز / توجو) ────────────────

    def _compute_fixed_fee(self, monthly_records):
        """
        نمط هنقرستيشين فرى / جاهز / توجو:
        - الشركة تستقطع مبلغاً ثابتاً من كل مندوب شهرياً (rider_monthly_fee)
        - باقي المستحقات تذهب للمزود أو للمندوب
        """
        self.ensure_one()
        contract = self.contract_id
        item_model = self.env['delivery.settlement.item']
        monthly_fee = contract.rider_monthly_fee or 0.0

        pricing_model = self.env['delivery.pricing.rule']
        all_rules = pricing_model.search([('contract_id', '=', contract.id)])
        pricing_rules = all_rules.filtered(lambda r: r.is_active)
        per_order_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'per_order')
        slab_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'tiered')
        monthly_target = self._get_monthly_target(
            self.period_start.month, self.period_start.year)
        valid_das_count = sum(1 for mp in monthly_records if getattr(mp, 'is_valid', False))

        total_orders = total_gross = total_order_base = 0.0
        total_cap = total_exp = total_sub = total_dxg = total_tips = 0.0
        total_penalties = total_vehicle_rental = total_monthly_fees = 0.0
        total_monthly_deduction = total_advance_deduction = 0.0
        total_provider_fee = 0.0
        valid_count = invalid_count = 0
        period_month = self.period_start.month
        period_year = self.period_start.year

        for mp in monthly_records:
            rider = mp.rider_id
            orders = mp.delivered_orders or 0
            rider_vehicle = rider.vehicle_type or 'motorcycle'
            is_valid = getattr(mp, 'is_valid', False)

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            order_base = 0.0
            if slab_rules:
                order_base = self._calc_tiered(slab_rules, orders, rider_vehicle)
            elif per_order_rules:
                order_base = self._calc_per_order(per_order_rules, orders, rider_vehicle)

            cap_incentive = getattr(mp, 'capacity_incentive', 0.0) or 0.0
            if not cap_incentive and monthly_target and is_valid:
                cap_incentive = self._calc_cap_incentive_from_target(
                    monthly_target, valid_das_count, rider_vehicle)
            exp_incentive = getattr(mp, 'experience_incentive', 0.0) or 0.0
            subsidy_val = getattr(mp, 'subsidy', 0.0) or 0.0
            dxg_val = getattr(mp, 'dxg', 0.0) or 0.0
            tips_val = getattr(mp, 'tips_excl_vat', 0.0) or 0.0
            other_val = getattr(mp, 'other_activities', 0.0) or 0.0
            deductions_val = getattr(mp, 'deductions', 0.0) or 0.0
            food_damage_val = getattr(mp, 'food_damage_compensation', 0.0) or 0.0
            other_adj_val = getattr(mp, 'other_adjustment', 0.0) or 0.0

            rider_penalties = abs(deductions_val) + abs(food_damage_val)
            rider_bonuses = other_val + other_adj_val

            gross = (order_base + cap_incentive + exp_incentive + subsidy_val
                     + dxg_val + tips_val + rider_bonuses - rider_penalties)

            vehicle_rental_deduction = 0.0
            if rider.vehicle_ownership == 'rented_from_company' and rider.vehicle_rental_amount > 0:
                vehicle_rental_deduction = rider.vehicle_rental_amount

            actual_monthly_fee = monthly_fee if monthly_fee > 0 else 0.0

            monthly_deduction, advance_deduction = self._get_rider_extra_deductions(
                rider, period_month, period_year)
            provider_fee = self._get_provider_fee(rider, period_month, period_year)

            item_model.create({
                'settlement_id': self.id,
                'rider_id': rider.id,
                'is_valid_da': is_valid,
                'orders': orders,
                'order_base_amount': order_base,
                'capacity_incentive': cap_incentive,
                'experience_incentive': exp_incentive,
                'subsidy': subsidy_val,
                'dxg': dxg_val,
                'tips_excl_vat': tips_val,
                'other_activities': other_val,
                'food_damage': food_damage_val,
                'penalties': rider_penalties,
                'bonuses': rider_bonuses,
                'adjustments': other_adj_val,
                'gross_amount': gross,
                'vehicle_rental_deduction': vehicle_rental_deduction,
                'subcontract_mgmt_fee': actual_monthly_fee,
                'provider_fee_deduction': provider_fee,
                'monthly_deduction': monthly_deduction,
                'advance_deduction': advance_deduction,
            })

            total_orders += orders
            total_gross += gross
            total_order_base += order_base
            total_cap += cap_incentive
            total_exp += exp_incentive
            total_sub += subsidy_val
            total_dxg += dxg_val
            total_tips += tips_val
            total_penalties += rider_penalties
            total_vehicle_rental += vehicle_rental_deduction
            total_monthly_fees += actual_monthly_fee
            total_monthly_deduction += monthly_deduction
            total_provider_fee += provider_fee
            total_advance_deduction += advance_deduction

        self.write({
            'total_orders': int(total_orders),
            'gross_amount': total_gross,
            'order_base_total': total_order_base,
            'capacity_incentive_total': total_cap,
            'experience_incentive_total': total_exp,
            'subsidy_total': total_sub,
            'dxg_total': total_dxg,
            'tips_total': total_tips,
            'penalties': total_penalties,
            'vehicle_rental_total': total_vehicle_rental,
            'subcontract_fee_total': total_monthly_fees,
            'provider_fee_total': total_provider_fee,
            'monthly_deduction_total': total_monthly_deduction,
            'advance_deduction_total': total_advance_deduction,
            'valid_rider_count': valid_count,
            'invalid_rider_count': invalid_count,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ── النمط المتقدم (الإعدادات القديمة - backward compatible) ──────────────

    def _compute_standard(self, monthly_records):
        """النمط المتقدم: يستخدم قواعد التسعير التقليدية (backward compatible)."""
        self.ensure_one()
        item_model = self.env['delivery.settlement.item']
        pricing_model = self.env['delivery.pricing.rule']

        period_month = self.period_start.month
        period_year = self.period_start.year
        monthly_target = self._get_monthly_target(period_month, period_year)

        all_contract_rules = pricing_model.search([('contract_id', '=', self.contract_id.id)])
        pricing_rules = all_contract_rules.filtered(lambda r: r.is_active)

        base_types = ('per_order', 'tiered', 'fixed_salary', 'per_distance', 'subcontract_fee')
        base_rules = pricing_rules.filtered(lambda r: r.pricing_type in base_types)

        if not base_rules:
            inactive_base = all_contract_rules.filtered(
                lambda r: r.pricing_type in base_types and not r.is_active)
            if inactive_base:
                names = ', '.join(inactive_base.mapped('name'))
                raise ValidationError(
                    f'العقد يحتوي على قواعد تسعير لكنها غير نشطة! فعّل واحدة منها أولاً:\n{names}')
            else:
                raise ValidationError(
                    'العقد لا يحتوي على أي قواعد تسعير!\n'
                    'اذهب إلى العقد واضغط "إنشاء القواعد الافتراضية" ثم فعّل القاعدة المناسبة.')

        per_order_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'per_order')
        slab_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'tiered')
        fixed_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'fixed_salary')
        per_km_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'per_distance')
        subcontract_fee_rules = pricing_rules.filtered(lambda r: r.pricing_type == 'subcontract_fee')

        valid_das_count = sum(1 for mp in monthly_records if getattr(mp, 'is_valid', False))

        total_orders = total_gross = total_order_base = 0.0
        total_cap = total_exp = total_sub = total_dxg = total_tips = 0.0
        total_penalties = total_vehicle_rental = total_subcontract_fees = 0.0
        total_monthly_deduction = total_advance_deduction = 0.0
        total_provider_fee = 0.0
        valid_count = invalid_count = 0
        period_month = self.period_start.month
        period_year = self.period_start.year

        for mp in monthly_records:
            rider = mp.rider_id
            orders = mp.delivered_orders or 0
            rider_vehicle = rider.vehicle_type or 'motorcycle'
            rider_type = rider.rider_type or 'internal'

            order_base = 0.0
            if slab_rules:
                order_base = self._calc_tiered(slab_rules, orders, rider_vehicle)
            elif per_order_rules:
                order_base = self._calc_per_order(per_order_rules, orders, rider_vehicle)
            elif per_km_rules:
                order_base = self._calc_per_distance(per_km_rules, mp, rider_vehicle)
            elif fixed_rules:
                order_base = self._calc_fixed_salary(fixed_rules, mp, rider_vehicle)

            cap_incentive = getattr(mp, 'capacity_incentive', 0.0) or 0.0
            if not cap_incentive and monthly_target and getattr(mp, 'is_valid', False):
                cap_incentive = self._calc_cap_incentive_from_target(
                    monthly_target, valid_das_count, rider_vehicle)
            exp_incentive = getattr(mp, 'experience_incentive', 0.0) or 0.0
            subsidy_val = getattr(mp, 'subsidy', 0.0) or 0.0
            dxg_val = getattr(mp, 'dxg', 0.0) or 0.0
            tips_val = getattr(mp, 'tips_excl_vat', 0.0) or 0.0
            other_val = getattr(mp, 'other_activities', 0.0) or 0.0
            deductions_val = getattr(mp, 'deductions', 0.0) or 0.0
            food_damage_val = getattr(mp, 'food_damage_compensation', 0.0) or 0.0
            other_adj_val = getattr(mp, 'other_adjustment', 0.0) or 0.0

            is_valid = getattr(mp, 'is_valid', False)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            rider_penalties = abs(deductions_val) + abs(food_damage_val)
            rider_bonuses = other_val + other_adj_val
            gross = (order_base + cap_incentive + exp_incentive + subsidy_val
                     + dxg_val + tips_val + rider_bonuses - rider_penalties)

            subcontract_mgmt_fee = 0.0
            if rider_type == 'subcontract' and subcontract_fee_rules:
                subcontract_mgmt_fee = max(0.0, self._calc_subcontract_fee(
                    subcontract_fee_rules, gross, order_base, rider_vehicle))

            vehicle_rental_deduction = 0.0
            if rider.vehicle_ownership == 'rented_from_company' and rider.vehicle_rental_amount > 0:
                vehicle_rental_deduction = rider.vehicle_rental_amount

            monthly_deduction, advance_deduction = self._get_rider_extra_deductions(
                rider, period_month, period_year)
            provider_fee = self._get_provider_fee(rider, period_month, period_year)

            item_model.create({
                'settlement_id': self.id,
                'rider_id': rider.id,
                'is_valid_da': is_valid,
                'orders': orders,
                'order_base_amount': order_base,
                'capacity_incentive': cap_incentive,
                'experience_incentive': exp_incentive,
                'subsidy': subsidy_val,
                'dxg': dxg_val,
                'tips_excl_vat': tips_val,
                'other_activities': other_val,
                'food_damage': food_damage_val,
                'penalties': rider_penalties,
                'bonuses': rider_bonuses,
                'adjustments': other_adj_val,
                'gross_amount': gross,
                'vehicle_rental_deduction': vehicle_rental_deduction,
                'subcontract_mgmt_fee': subcontract_mgmt_fee,
                'provider_fee_deduction': provider_fee,
                'monthly_deduction': monthly_deduction,
                'advance_deduction': advance_deduction,
            })

            total_orders += orders
            total_gross += gross
            total_order_base += order_base
            total_cap += cap_incentive
            total_exp += exp_incentive
            total_sub += subsidy_val
            total_dxg += dxg_val
            total_tips += tips_val
            total_penalties += rider_penalties
            total_vehicle_rental += vehicle_rental_deduction
            total_subcontract_fees += subcontract_mgmt_fee
            total_monthly_deduction += monthly_deduction
            total_provider_fee += provider_fee
            total_advance_deduction += advance_deduction

        self.write({
            'total_orders': int(total_orders),
            'gross_amount': total_gross,
            'order_base_total': total_order_base,
            'capacity_incentive_total': total_cap,
            'experience_incentive_total': total_exp,
            'subsidy_total': total_sub,
            'dxg_total': total_dxg,
            'tips_total': total_tips,
            'penalties': total_penalties,
            'vehicle_rental_total': total_vehicle_rental,
            'subcontract_fee_total': total_subcontract_fees,
            'provider_fee_total': total_provider_fee,
            'monthly_deduction_total': total_monthly_deduction,
            'advance_deduction_total': total_advance_deduction,
            'valid_rider_count': valid_count,
            'invalid_rider_count': invalid_count,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_generate_payslips(self):
        """Generate a payslip batch from the approved settlement."""
        self.ensure_one()
        if self.status not in ('approved', 'locked'):
            raise ValidationError(
                'يمكن إنشاء كشوف الرواتب فقط للتسويات المعتمدة أو المقفلة.\n'
                'Payslips can only be generated for approved or locked settlements.'
            )

        struct = self.env.ref('delivery_3pl.salary_structure_3pl_delivery', raise_if_not_found=False)
        input_earn = self.env.ref('delivery_3pl.input_type_delivery_earn', raise_if_not_found=False)
        input_vehicle = self.env.ref('delivery_3pl.input_type_vehicle_rent', raise_if_not_found=False)
        input_subcontract = self.env.ref('delivery_3pl.input_type_subcontract_fee', raise_if_not_found=False)
        input_penalty = self.env.ref('delivery_3pl.input_type_delivery_penalty', raise_if_not_found=False)
        input_bonus = self.env.ref('delivery_3pl.input_type_delivery_bonus', raise_if_not_found=False)

        run_name = f'3PL Settlement — {self.settlement_number} ({self.period_start} → {self.period_end})'
        run = self.env['hr.payslip.run'].create({
            'name': run_name,
            'date_start': self.period_start,
            'date_end': self.period_end,
        })
        self.payslip_run_id = run.id

        payslips_created = 0
        riders_without_employee = []

        for item in self.item_ids:
            rider = item.rider_id
            if not rider.employee_id:
                riders_without_employee.append(rider.name or rider.name_ar or str(rider.id))
                continue

            input_lines = []
            if input_earn and item.gross_amount:
                input_lines.append((0, 0, {
                    'input_type_id': input_earn.id,
                    'amount': item.gross_amount,
                    'name': 'Order Earnings (أرباح الطلبات)',
                }))
            if input_vehicle and item.vehicle_rental_deduction:
                input_lines.append((0, 0, {
                    'input_type_id': input_vehicle.id,
                    'amount': item.vehicle_rental_deduction,
                    'name': 'Vehicle Rental (إيجار المركبة)',
                }))
            if input_subcontract and item.subcontract_mgmt_fee:
                input_lines.append((0, 0, {
                    'input_type_id': input_subcontract.id,
                    'amount': item.subcontract_mgmt_fee,
                    'name': 'Subcontract Management Fee (رسوم الإدارة)',
                }))
            if input_penalty and item.penalties:
                input_lines.append((0, 0, {
                    'input_type_id': input_penalty.id,
                    'amount': item.penalties,
                    'name': 'Penalties (الغرامات)',
                }))
            if input_bonus and item.bonuses:
                input_lines.append((0, 0, {
                    'input_type_id': input_bonus.id,
                    'amount': item.bonuses,
                    'name': 'Bonuses (المكافآت)',
                }))

            payslip_vals = {
                'employee_id': rider.employee_id.id,
                'date_from': self.period_start,
                'date_to': self.period_end,
                'payslip_run_id': run.id,
                'name': f'3PL — {rider.name or rider.employee_id.name} — {self.settlement_number}',
                'input_line_ids': input_lines,
            }
            if struct:
                payslip_vals['struct_id'] = struct.id

            self.env['hr.payslip'].create(payslip_vals)
            payslips_created += 1

        msg_parts = [
            f'<b>Payslip Batch Created / تم إنشاء دفعة كشوف الرواتب</b>',
            f'Batch: {run.name}',
            f'Payslips created: {payslips_created}',
        ]
        if riders_without_employee:
            msg_parts.append(
                f'<br/>⚠️ Riders without linked employee (skipped): {", ".join(riders_without_employee)}'
            )
        self.message_post(body='<br/>'.join(msg_parts))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payslip Batch / دفعة كشوف الرواتب',
            'res_model': 'hr.payslip.run',
            'res_id': run.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_payslips(self):
        self.ensure_one()
        if not self.payslip_run_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payslips',
            'res_model': 'hr.payslip',
            'view_mode': 'list,form',
            'domain': [('payslip_run_id', '=', self.payslip_run_id.id)],
        }

    def action_submit_for_approval(self):
        self.ensure_one()
        if self.status != 'draft':
            raise ValidationError('Only draft settlements can be submitted for approval.')
        self.write({'status': 'pending_approval'})

    def action_approve(self):
        self.ensure_one()
        if self.status != 'pending_approval':
            raise ValidationError('Only pending settlements can be approved.')
        self.write({
            'status': 'approved',
            'approved_by': self.env.user.id,
            'approved_at': fields.Datetime.now(),
        })
        # ── إعادة ضبط السلفة على المناديب الذين خُصمت سلفتهم ────────────────
        for item in self.item_ids:
            if item.advance_deduction > 0 and item.rider_id.advance_paid:
                item.rider_id.sudo().write({'advance_amount': 0.0, 'advance_paid': False})

    def action_lock(self):
        self.ensure_one()
        if self.status != 'approved':
            raise ValidationError('Only approved settlements can be locked.')
        self.write({'status': 'locked'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.status == 'locked':
            raise ValidationError('Locked settlements cannot be reset.')
        self.write({
            'status': 'draft',
            'approved_by': False,
            'approved_at': False,
        })

    def action_print_settlement(self):
        self.ensure_one()
        return self.env.ref('delivery_3pl.action_report_settlement').report_action(self)


class DeliverySettlementItem(models.Model):
    _name = 'delivery.settlement.item'
    _description = 'Settlement Line Item (Per Rider)'
    _order = 'rider_id'

    settlement_id = fields.Many2one('delivery.settlement', string='Settlement', required=True, ondelete='cascade')
    rider_id = fields.Many2one('delivery.rider', string='Rider', required=True)
    is_valid_da = fields.Boolean(string='Valid DA (صالح)', default=False)
    validity_reason = fields.Char(string='Validity Reason')

    orders = fields.Integer(string='Orders', default=0)
    gross_amount = fields.Float(string='Gross Amount', digits=(12, 2), default=0.0)

    order_base_amount = fields.Float(string='Order Base Pricing', digits=(12, 2), default=0.0)
    capacity_incentive = fields.Float(string='Capacity Incentive (حوافز سعة الطلب)', digits=(12, 2), default=0.0)
    experience_incentive = fields.Float(string='Experience Incentive (حوافز التسليم)', digits=(12, 2), default=0.0)
    subsidy = fields.Float(string='Subsidy (الإعانة)', digits=(12, 2), default=0.0)
    dxg = fields.Float(string='DXG', digits=(12, 2), default=0.0)
    other_activities = fields.Float(string='Other Activities (الأنشطة والمكافآت)', digits=(12, 2), default=0.0)
    food_damage = fields.Float(string='Food Damage (تعويض تلف الطعام)', digits=(12, 2), default=0.0,
                                help='Negative value')
    tips_excl_vat = fields.Float(string='Tips excl. VAT (البقشيش)', digits=(12, 2), default=0.0)

    penalties = fields.Float(string='Penalties', digits=(12, 2), default=0.0)
    bonuses = fields.Float(string='Bonuses', digits=(12, 2), default=0.0)
    deposits = fields.Float(string='Deposits', digits=(12, 2), default=0.0)
    adjustments = fields.Float(string='Adjustments', digits=(12, 2), default=0.0)

    vehicle_rental_deduction = fields.Float(
        string='Vehicle Rental Deduction (اقتطاع إيجار المركبة)',
        digits=(12, 2), default=0.0,
        help='Monthly vehicle rental deducted from rider net pay (rented_from_company).',
    )
    subcontract_mgmt_fee = fields.Float(
        string='Subcontract Management Fee (رسوم إدارة المقاول)',
        digits=(12, 2), default=0.0,
        help='Management fee deducted from subcontract rider gross earnings.',
    )
    provider_fee_deduction = fields.Float(
        string='خصم مزود الخدمة (Service Provider Fee)',
        digits=(12, 2), default=0.0,
        help='المبلغ الشهري المستقطع لصالح الشركة المزودة للخدمة من مستحقات المندوب الفرى لانسر. '
             'يُحتسب تناسبياً بالأيام إذا استلم المندوب الـ ID خلال شهر التسوية.',
    )
    monthly_deduction = fields.Float(
        string='استقطاعات شهرية (Monthly Deduction)',
        digits=(12, 2), default=0.0,
        help='مجموع استقطاعات المندوب الشهرية من سجل delivery.rider.deduction '
             '(إيجار، سكن، بنزين، قسط سيارة، سلف، تغذية، أخرى)',
    )
    advance_deduction = fields.Float(
        string='استرداد السلفة (Advance Deduction)',
        digits=(12, 2), default=0.0,
        help='مبلغ السلفة المقدمة المستقطع من مستحقات المندوب هذا الشهر. '
             'يُصفَّر تلقائياً على المندوب عند اعتماد التسوية.',
    )

    net_amount = fields.Float(string='Net Amount', digits=(12, 2), default=0.0,
                              compute='_compute_net_amount', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('gross_amount', 'penalties', 'bonuses', 'deposits', 'adjustments',
                 'vehicle_rental_deduction', 'subcontract_mgmt_fee', 'provider_fee_deduction',
                 'monthly_deduction', 'advance_deduction')
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = (
                rec.gross_amount
                - rec.penalties
                + rec.bonuses
                - rec.deposits
                + rec.adjustments
                - rec.vehicle_rental_deduction
                - rec.subcontract_mgmt_fee
                - rec.provider_fee_deduction
                - rec.monthly_deduction
                - rec.advance_deduction
            )
