"""
Migration script: 18.0.4.5.0 → 18.0.4.5.1

Changes:
- delivery.import.session: import_all_sheets (Boolean) — استيراد كل الأوراق دفعة واحدة
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info('delivery_3pl v4.5.1 pre-migration: adding import_all_sheets column...')

    cr.execute("""
        ALTER TABLE delivery_import_session
        ADD COLUMN IF NOT EXISTS import_all_sheets BOOLEAN DEFAULT FALSE;
    """)

    _logger.info('delivery_3pl v4.5.1 pre-migration: done.')
