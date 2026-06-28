from odoo import models, fields, api


class DeliveryRiderType(models.Model):
    _name = 'delivery.rider.type'
    _description = 'Rider Type'
    _order = 'name'

    name = fields.Char(string='Type Name (EN)', required=True)
    name_ar = fields.Char(string='Type Name (AR)')
    type = fields.Selection([
        ('internal', 'Internal Rider'),
        ('subcontract', 'Subcontract Rider'),
    ], string='Type', default='internal', required=True)
    has_deposit = fields.Boolean(string='Requires Deposit', default=False)
    has_penalties = fields.Boolean(string='Has Penalties', default=True)
    has_wallet = fields.Boolean(string='Has Wallet', default=True)
    description = fields.Text(string='Description')


class DeliveryRider(models.Model):
    _name = 'delivery.rider'
    _description = 'Delivery Rider (Independent Contractor)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    active = fields.Boolean(string='نشط (Active)', default=True, tracking=True)

    name = fields.Char(string='Full Name (EN)', tracking=True)
    name_ar = fields.Char(string='Full Name (AR)')
    phone = fields.Char(string='Phone Number', required=True, tracking=True)
    national_id = fields.Char(string='National ID / Iqama', tracking=True)
    platform_account_id = fields.Char(string='Platform Account ID (معرف الحساب)', tracking=True,
                                       help='Account ID on the delivery platform (e.g. Keeta account ID)')
    rider_type_id = fields.Many2one('delivery.rider.type', string='Rider Type', tracking=True)
    rider_type = fields.Selection(related='rider_type_id.type', string='Type Category', store=True)
    primary_company_id = fields.Many2one('delivery.company', string='Primary Company', tracking=True)
    branch_id = fields.Many2one('delivery.company.branch', string='Branch', tracking=True,
                                 domain="[('company_id', '=', primary_company_id)]")
    city_id = fields.Many2one('delivery.city', string='City', tracking=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ], string='Status', default='active', required=True, tracking=True)

    # ── الشركة المزودة للخدمة (فرى لانسر) ───────────────────────────────────
    service_provider_id = fields.Many2one(
        'delivery.service.provider',
        string='الشركة المزودة للخدمة (Service Provider)',
        tracking=True,
        help='الشركة التي يعمل تحتها هذا المندوب كفرى لانسر. تُستخدم في احتساب المستحقات وصافي مزود الخدمة.',
    )

    # ── الكفالة ومستلم الـ ID ────────────────────────────────────────────────
    is_kafala = fields.Boolean(
        string='كفالة (Kafala)',
        default=False,
        tracking=True,
        help='المندوب مسجّل على نظام الكفالة (صاحب حساب المنصة الأساسي).',
    )
    id_recipient_id = fields.Many2one(
        'delivery.rider',
        string='مستلم الـ ID (ID Recipient)',
        tracking=True,
        index=True,
        domain="[('active', '=', True)]",
        help='المندوب (الفرى لانسر) الذي استلم حساب الـ ID فعلياً ويعمل عليه. '
             'يظهر عند تفعيل خانة "كفالة".',
    )
    id_receipt_date = fields.Date(
        string='تاريخ استلام الـ ID (ID Receipt Date)',
        tracking=True,
        help='تاريخ استلام المندوب لحساب الـ ID. يُستخدم لاحتساب خصم مزود الخدمة '
             'بشكل تناسبي بالأيام في شهر الاستلام.',
    )

    # ── السلفة المقدمة ────────────────────────────────────────────────────────
    advance_paid = fields.Boolean(
        string='دفع مبلغ مقدماً؟',
        default=False,
        tracking=True,
        help='هل دُفع مبلغ السلفة المقدمة لهذا المندوب؟',
    )
    advance_amount = fields.Float(
        string='مبلغ السلفة المقدمة (ريال)',
        digits=(12, 2),
        default=0.0,
        tracking=True,
        help='المبلغ الذي صُرف للمندوب مقدماً قبل التسوية الشهرية.',
    )

    # ── HR Employee Link (for payslip generation) ────────────────────────────
    employee_id = fields.Many2one(
        'hr.employee',
        string='Linked Employee (الموظف المرتبط)',
        tracking=True,
        copy=False,
        help='Link this rider to an HR employee record to enable payslip generation from settlements.',
    )

    # ── Vehicle Info ─────────────────────────────────────────────────────────
    vehicle_type = fields.Selection([
        ('car', 'Car (Private Car)'),
        ('motorcycle', 'Motorcycle / Bike'),
    ], string='Vehicle Type', tracking=True)
    license_plate = fields.Char(string='License Plate (رقم اللوحة)', tracking=True)
    vehicle_model = fields.Char(string='Vehicle Model (موديل المركبة)', tracking=True,
                                help='اسم وموديل المركبة، مثال: تويوتا يارس 2022')
    vehicle_year = fields.Integer(string='Vehicle Year (سنة الصنع)', tracking=True)
    vehicle_ownership = fields.Selection([
        ('company_owned', 'ملك الشركة (Company Asset)'),
        ('rented_from_company', 'مؤجرة من الشركة (Rented from Company)'),
        ('rider_owned', 'ملك السائق (Rider-Owned)'),
    ], string='Vehicle Ownership (ملكية المركبة)', default='company_owned', tracking=True,
        help='company_owned: الشركة تملك المركبة وتسلمها للسائق\n'
             'rented_from_company: السائق يستأجرها من الشركة مقابل رسوم\n'
             'rider_owned: المركبة ملك السائق الشخصي')

    # ── Fleet Vehicle Link ───────────────────────────────────────────────────
    fleet_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Fleet Vehicle (مركبة الأسطول)',
        tracking=True,
        copy=False,
        help='Link this rider to the company fleet vehicle they operate.\n'
             'Applicable when vehicle is company-owned or rented from company.',
        domain="[('state_id.name', '!=', 'Archived')]",
    )

    # ── Vehicle Rental ───────────────────────────────────────────────────────
    vehicle_rental_amount = fields.Float(
        string='Monthly Vehicle Rental (SAR) (إيجار المركبة الشهري)',
        digits=(12, 2),
        default=0.0,
        tracking=True,
        help='Monthly rental amount deducted from rider settlement when vehicle_ownership is "Rented from Company".',
    )

    join_date = fields.Date(string='Join Date')
    work_start_date = fields.Date(string='Work Start Date (تاريخ بداية العمل)', tracking=True)
    work_end_date = fields.Date(string='Work End Date (تاريخ نهاية العمل)', tracking=True)

    parent_rider_id = fields.Many2one(
        'delivery.rider',
        string='المندوب الرئيسي (Parent Rider)',
        index=True,
        domain="[('active', '=', True), ('primary_company_id', '=', primary_company_id)]",
        help='إذا كان هذا السائق فرىلانسر يعمل تحت حساب سائق آخر (البيرنت).\n'
             'يُسمح بتكرار نفس البيرنت لعدة سائقين فرىلانسر.\n'
             'If this rider is a freelancer working under another rider account (parent). '
             'Multiple freelancers can share the same parent rider.',
    )
    sub_rider_ids = fields.One2many(
        'delivery.rider', 'parent_rider_id',
        string='Sub-Riders / Freelancers (فرىلانسر)',
    )

    active_company_ids = fields.Many2many('delivery.company', 'delivery_rider_company_rel',
                                           'rider_id', 'company_id',
                                           string='Active Platforms (التطبيقات النشطة)',
                                           help='التطبيقات / الشركات التي يعمل عليها هذا المندوب حالياً')
    active_platform_count = fields.Integer(string='# Platforms', compute='_compute_platform_count', store=True)
    all_platforms_covered = fields.Boolean(string='All Platforms Covered', compute='_compute_all_platforms_covered', store=True,
                                            help='المندوب يعمل على جميع التطبيقات المتاحة')
    available_platform_names = fields.Char(string='Platforms', compute='_compute_platform_display')
    missing_platform_names = fields.Char(string='Missing Platforms', compute='_compute_platform_display')

    # ── تعدد الفروع والعقود ──────────────────────────────────────────────
    active_branch_ids = fields.Many2many(
        'delivery.company.branch',
        'delivery_rider_branch_rel',
        'rider_id', 'branch_id',
        string='Active Branches / Contracts (الفروع والعقود النشطة)',
        help='جميع الفروع التي يعمل بها هذا المندوب. '
             'يمكن للمندوب من نوع "داخلي" العمل في أكثر من فرع (عقد) بنفس الوقت. '
             'سجلات الأداء اليومي والشهري والتسوية تُنشأ لكل فرع بشكل مستقل.'
    )
    active_branch_count = fields.Integer(
        string='# Active Branches',
        compute='_compute_active_branch_count',
        store=True,
    )

    @api.depends('active_branch_ids')
    def _compute_active_branch_count(self):
        for rec in self:
            rec.active_branch_count = len(rec.active_branch_ids)

    # ── مزامنة التطبيقات النشطة تلقائياً من الفروع ───────────────────────
    @api.onchange('active_branch_ids', 'primary_company_id')
    def _onchange_sync_active_companies(self):
        companies = self.active_branch_ids.mapped('company_id')
        if self.primary_company_id:
            companies |= self.primary_company_id
        self.active_company_ids = companies

    def _sync_active_companies(self):
        for rec in self:
            companies = rec.active_branch_ids.mapped('company_id')
            if rec.primary_company_id:
                companies |= rec.primary_company_id
            if set(companies.ids) != set(rec.active_company_ids.ids):
                rec.active_company_ids = companies

    def write(self, vals):
        result = super().write(vals)
        if 'active_branch_ids' in vals or 'primary_company_id' in vals:
            self._sync_active_companies()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_active_companies()
        return records

    def action_sync_platforms_from_branches(self):
        self._sync_active_companies()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تمت المزامنة / Sync Complete',
                'message': 'تم تحديث التطبيقات النشطة من الفروع بنجاح.',
                'type': 'success',
                'sticky': False,
            }
        }

    # ── أرشفة المندوب ────────────────────────────────────────────────────────
    def action_archive_rider(self):
        """أرشفة المندوب: ضبط active=False وتحرير platform_account_id للإعادة الاستخدام."""
        for rec in self:
            rec.write({
                'active': False,
                'status': 'inactive',
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تمت الأرشفة',
                'message': f'تم أرشفة {len(self)} مندوب. يمكن استعادتهم من خلال فلتر "المؤرشفون".',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_unarchive_rider(self):
        """استعادة المندوب المؤرشف."""
        for rec in self:
            rec.write({
                'active': True,
                'status': 'active',
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تمت الاستعادة',
                'message': f'تم استعادة {len(self)} مندوب.',
                'type': 'success',
                'sticky': False,
            }
        }

    # ── Onchange: vehicle ownership → clear/suggest fleet & rental ───────────
    @api.onchange('vehicle_ownership')
    def _onchange_vehicle_ownership(self):
        if self.vehicle_ownership == 'rider_owned':
            self.fleet_vehicle_id = False
            self.vehicle_rental_amount = 0.0
        elif self.vehicle_ownership == 'company_owned':
            self.vehicle_rental_amount = 0.0

    @api.onchange('fleet_vehicle_id')
    def _onchange_fleet_vehicle_id(self):
        if self.fleet_vehicle_id:
            vehicle = self.fleet_vehicle_id
            if vehicle.license_plate and not self.license_plate:
                self.license_plate = vehicle.license_plate
            if vehicle.model_id and not self.vehicle_model:
                self.vehicle_model = vehicle.model_id.display_name
            if hasattr(vehicle, 'model_year') and vehicle.model_year and not self.vehicle_year:
                self.vehicle_year = vehicle.model_year

    is_self_delivery = fields.Boolean(string='Self Delivery Rider', default=True, tracking=True,
                                       help='Rider is compliant (Ajeer Share/Sponsored/Saudi)')
    is_valid_da = fields.Boolean(string='Valid DA (صالح)', default=False, tracking=True)
    validity_reason = fields.Char(string='Validity Reason / Status', tracking=True)
    experience_score = fields.Float(string='Experience Score', digits=(8, 4), tracking=True)
    performance_level = fields.Selection([
        ('A', 'Level A'),
        ('B', 'Level B'),
        ('C', 'Level C'),
        ('D', 'Level D'),
    ], string='Performance Level', tracking=True)
    valid_days_count = fields.Integer(string='Valid Days (T-Valid)', tracking=True)
    facial_verification_pass = fields.Boolean(string='Facial Verification Passed', default=True)

    wallet_balance = fields.Float(string='Wallet Balance', digits=(12, 2), default=0.0)
    deposit_amount = fields.Float(string='Deposit Amount', digits=(12, 2), default=0.0)
    notes = fields.Text(string='Notes')

    wallet_transaction_ids = fields.One2many('delivery.wallet.transaction', 'rider_id', string='Wallet Transactions')
    penalty_ids = fields.One2many('delivery.rider.penalty', 'rider_id', string='Penalties')
    settlement_item_ids = fields.One2many('delivery.settlement.item', 'rider_id', string='Settlement Items')
    daily_performance_ids = fields.One2many('delivery.daily.performance', 'rider_id', string='Daily Performance')
    monthly_performance_ids = fields.One2many('delivery.monthly.performance', 'rider_id', string='Monthly Performance')
    deduction_ids = fields.One2many('delivery.rider.deduction', 'rider_id', string='Deductions')

    penalty_count = fields.Integer(compute='_compute_penalty_count')
    transaction_count = fields.Integer(compute='_compute_transaction_count')
    daily_perf_count = fields.Integer(compute='_compute_daily_perf_count')
    monthly_perf_count = fields.Integer(compute='_compute_monthly_perf_count')

    def _compute_penalty_count(self):
        for rec in self:
            rec.penalty_count = len(rec.penalty_ids)

    def _compute_transaction_count(self):
        for rec in self:
            rec.transaction_count = len(rec.wallet_transaction_ids)

    def _compute_daily_perf_count(self):
        for rec in self:
            rec.daily_perf_count = len(rec.daily_performance_ids)

    def _compute_monthly_perf_count(self):
        for rec in self:
            rec.monthly_perf_count = len(rec.monthly_performance_ids)

    @api.depends('active_company_ids')
    def _compute_platform_count(self):
        for rec in self:
            rec.active_platform_count = len(rec.active_company_ids)

    @api.depends('active_company_ids')
    def _compute_all_platforms_covered(self):
        total_active = self.env['delivery.company'].search_count([('is_active', '=', True)])
        for rec in self:
            rec.all_platforms_covered = len(rec.active_company_ids) >= total_active if total_active > 0 else False

    def _compute_platform_display(self):
        all_companies = self.env['delivery.company'].search([('is_active', '=', True)])
        for rec in self:
            active = rec.active_company_ids
            rec.available_platform_names = ', '.join(active.mapped('name')) if active else ''
            missing = all_companies - active
            rec.missing_platform_names = ', '.join(missing.mapped('name')) if missing else ''

    def name_get(self):
        result = []
        for rec in self:
            label = rec.name or rec.name_ar or rec.platform_account_id or 'Rider'
            if rec.name and rec.name_ar:
                label = f"{rec.name} / {rec.name_ar}"
            elif rec.name_ar and not rec.name:
                label = rec.name_ar
            # ── حالة الكفالة: اسم صاحب الحساب + اسم مستلم الـ ID إن وُجد ──────
            if rec.is_kafala and rec.id_recipient_id:
                recipient = rec.id_recipient_id
                recipient_name = recipient.name or recipient.name_ar or 'مستلم'
                label = f"{label} ← {recipient_name}"
            if rec.platform_account_id:
                label = f"{label} [{rec.platform_account_id}]"
            valid_tag = " ✓" if rec.is_valid_da else ""
            result.append((rec.id, f"{label}{valid_tag}"))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            name_stripped = str(name).strip()
            riders = self.search(
                [('platform_account_id', '=', name_stripped)] + args, limit=1)
            if not riders:
                riders = self.search(
                    [('phone', '=', name_stripped)] + args, limit=1)
            if not riders:
                riders = self.search([
                    '|', '|',
                    ('name', operator, name_stripped),
                    ('name_ar', operator, name_stripped),
                    ('platform_account_id', operator, name_stripped),
                ] + args, limit=limit)
            if not riders and operator == '=':
                riders = self.search([
                    '|', '|',
                    ('name', 'ilike', name_stripped),
                    ('name_ar', 'ilike', name_stripped),
                    ('platform_account_id', 'ilike', name_stripped),
                ] + args, limit=limit)
            if len(riders) > 1 and operator == '=':
                riders = riders[:1]
            return riders.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.onchange('primary_company_id')
    def _onchange_company_id(self):
        if self.primary_company_id:
            self.branch_id = False

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            self.city_id = self.branch_id.city_id

    def action_view_wallet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Wallet - {self.name}',
            'res_model': 'delivery.wallet.transaction',
            'view_mode': 'list,form',
            'domain': [('rider_id', '=', self.id)],
            'context': {'default_rider_id': self.id},
        }

    def action_view_penalties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Penalties - {self.name}',
            'res_model': 'delivery.rider.penalty',
            'view_mode': 'list,form',
            'domain': [('rider_id', '=', self.id)],
            'context': {'default_rider_id': self.id},
        }

    def action_view_daily_performance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Daily Performance - {self.name}',
            'res_model': 'delivery.daily.performance',
            'view_mode': 'list,form',
            'domain': [('rider_id', '=', self.id)],
            'context': {'default_rider_id': self.id},
        }

    def action_view_monthly_performance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Monthly Performance - {self.name}',
            'res_model': 'delivery.monthly.performance',
            'view_mode': 'list,form',
            'domain': [('rider_id', '=', self.id)],
            'context': {'default_rider_id': self.id},
        }
