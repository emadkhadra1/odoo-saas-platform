from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DeliverySettlementBatchWizard(models.TransientModel):
    _name = 'delivery.settlement.batch.wizard'
    _description = 'Batch Settlement Computation Wizard (احتساب تسويات دفعية)'

    # ── بيانات الفترة ────────────────────────────────────────────────────────
    company_id = fields.Many2one(
        'delivery.company',
        string='الشركة / Company',
        required=True,
    )
    branch_id = fields.Many2one(
        'delivery.company.branch',
        string='الفرع / Branch',
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    period_start = fields.Date(string='بداية الفترة / Period Start', required=True)
    period_end = fields.Date(string='نهاية الفترة / Period End', required=True)
    cycle = fields.Selection([
        ('weekly', 'Weekly (أسبوعي)'),
        ('semi_monthly', 'Semi-Monthly (نصف شهري)'),
        ('monthly', 'Monthly (شهري)'),
    ], string='دورة التسوية / Cycle', default='monthly', required=True)

    # ── العقود المؤهلة ────────────────────────────────────────────────────────
    contract_ids = fields.Many2many(
        'delivery.contract',
        'batch_wizard_contract_rel',
        'wizard_id',
        'contract_id',
        string='العقود النشطة / Active Contracts',
        help='سيُنشأ تسوية منفصلة لكل عقد من هذه العقود. يمكنك إلغاء اختيار أي عقد.',
    )

    # ── النتائج ───────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'تحديد المعطيات'),
        ('done', 'اكتملت العملية'),
    ], default='draft', string='الحالة')

    computation_log = fields.Text(
        string='سجل الاحتساب / Computation Log',
        readonly=True,
    )
    created_settlement_ids = fields.Many2many(
        'delivery.settlement',
        'batch_wizard_settlement_rel',
        'wizard_id',
        'settlement_id',
        string='التسويات المُنشأة',
        readonly=True,
    )

    # ── onchange: تحميل العقود تلقائياً ───────────────────────────────────────
    @api.onchange('company_id', 'branch_id')
    def _onchange_company_branch(self):
        if not self.company_id:
            self.contract_ids = [(5, 0, 0)]
            return
        domain = [
            ('company_id', '=', self.company_id.id),
            ('status', '=', 'active'),
        ]
        if self.branch_id:
            domain += ['|',
                       ('branch_id', '=', self.branch_id.id),
                       ('branch_id', '=', False)]
        self.contract_ids = self.env['delivery.contract'].search(domain)

    # ── تحميل العقود (زر يدوي) ────────────────────────────────────────────────
    def action_load_contracts(self):
        self.ensure_one()
        self._onchange_company_branch()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement.batch.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    # ── الاحتساب الدفعي ───────────────────────────────────────────────────────
    def action_compute_batch(self):
        self.ensure_one()

        if not self.contract_ids:
            raise ValidationError(
                'لا توجد عقود مُختارة!\n'
                'اضغط "تحديث العقود" أولاً أو اختر عقوداً يدوياً.'
            )

        _MONTHS = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر',
        }
        period_month = self.period_start.month
        period_year = self.period_start.year
        period_label = f"{_MONTHS[period_month]}-{period_year}"

        Settlement = self.env['delivery.settlement']
        created_ids = []
        log_lines = [f'⚙️  احتساب دفعي — {period_label} | {self.branch_id.name}', '']

        for contract in self.contract_ids:
            cnum = contract.contract_number or str(contract.id)
            cname = contract.name or cnum

            # التحقق من وجود تسوية سابقة لنفس العقد والفترة
            existing = Settlement.search([
                ('contract_id', '=', contract.id),
                ('period_start', '=', self.period_start),
            ], limit=1)
            if existing:
                log_lines.append(
                    f'⚠️  [{cnum}] {cname} — '
                    f'تسوية موجودة مسبقاً: {existing.settlement_number} ({existing.status})'
                )
                continue

            # توليد رقم التسوية تلقائياً
            settlement_number = f'{period_label}-{cnum}'

            new_settlement = Settlement.create({
                'company_id': self.company_id.id,
                'branch_id': self.branch_id.id,
                'contract_id': contract.id,
                'settlement_number': settlement_number,
                'period_start': self.period_start,
                'period_end': self.period_end,
                'cycle': self.cycle,
                'status': 'draft',
            })

            try:
                new_settlement.action_compute_settlement()
                created_ids.append(new_settlement.id)
                log_lines.append(
                    f'✅  [{cnum}] {cname} — '
                    f'تم | {new_settlement.valid_rider_count} مندوب صالح | '
                    f'صافي: {new_settlement.net_amount:,.2f} ريال'
                )
            except Exception as exc:
                log_lines.append(f'❌  [{cnum}] {cname} — خطأ: {exc}')
                new_settlement.unlink()

        if not created_ids and not any('✅' in l for l in log_lines):
            summary = '\n'.join(log_lines)
            raise ValidationError(summary)

        log_lines.append('')
        log_lines.append(
            f'📊  النتيجة: أُنشئت {len(created_ids)} تسوية من أصل '
            f'{len(self.contract_ids)} عقد.'
        )

        self.write({
            'state': 'done',
            'computation_log': '\n'.join(log_lines),
            'created_settlement_ids': [(6, 0, created_ids)],
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.settlement.batch.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    # ── فتح التسويات المُنشأة ─────────────────────────────────────────────────
    def action_view_settlements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'التسويات المُنشأة / Created Settlements',
            'res_model': 'delivery.settlement',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.created_settlement_ids.ids)],
            'target': 'current',
        }
