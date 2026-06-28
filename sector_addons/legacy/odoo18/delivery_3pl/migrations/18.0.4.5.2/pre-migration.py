"""
Migration script: 18.0.4.5.1 → 18.0.4.5.2

Changes:
- delivery.settlement.item : monthly_deduction  — استقطاعات شهرية (من delivery.rider.deduction)
- delivery.settlement.item : advance_deduction  — استرداد السلفة المقدمة
- delivery.settlement      : monthly_deduction_total — إجمالي الاستقطاعات الشهرية
- delivery.settlement      : advance_deduction_total  — إجمالي السلف المستردة
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info('delivery_3pl v4.5.2 pre-migration: adding deduction columns...')

    cr.execute("""
        ALTER TABLE delivery_settlement_item
        ADD COLUMN IF NOT EXISTS monthly_deduction NUMERIC(12,2) DEFAULT 0.0,
        ADD COLUMN IF NOT EXISTS advance_deduction  NUMERIC(12,2) DEFAULT 0.0;
    """)

    cr.execute("""
        ALTER TABLE delivery_settlement
        ADD COLUMN IF NOT EXISTS monthly_deduction_total NUMERIC(12,2) DEFAULT 0.0,
        ADD COLUMN IF NOT EXISTS advance_deduction_total  NUMERIC(12,2) DEFAULT 0.0;
    """)

    _logger.info('delivery_3pl v4.5.2 pre-migration: done.')
