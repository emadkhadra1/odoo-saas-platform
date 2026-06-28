"""
Migration script: 18.0.4.4.0 → 18.0.4.5.0

New features:
- delivery.service.provider model (شركة مزودة خدمة)
- delivery.rider: active, service_provider_id, advance_paid, advance_amount
- delivery.contract: hungerstation_internal pricing mode + keeta mode + new config fields
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info('delivery_3pl v4.5.0 pre-migration: adding new columns...')

    # delivery.rider — حقل active (الأرشفة)
    cr.execute("""
        ALTER TABLE delivery_rider
        ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE;
    """)

    # delivery.rider — service_provider_id
    cr.execute("""
        ALTER TABLE delivery_rider
        ADD COLUMN IF NOT EXISTS service_provider_id INTEGER;
    """)

    # delivery.rider — advance_paid / advance_amount
    cr.execute("""
        ALTER TABLE delivery_rider
        ADD COLUMN IF NOT EXISTS advance_paid BOOLEAN DEFAULT FALSE;
    """)
    cr.execute("""
        ALTER TABLE delivery_rider
        ADD COLUMN IF NOT EXISTS advance_amount NUMERIC(12,2) DEFAULT 0.0;
    """)

    # delivery.contract — hungerstation internal fields
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS hs_target_orders INTEGER DEFAULT 550;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS hs_base_salary NUMERIC(12,2) DEFAULT 1500.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS hs_rate_above_target NUMERIC(12,2) DEFAULT 8.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS hs_rate_below_target NUMERIC(12,2) DEFAULT 4.0;
    """)

    # delivery.contract — keeta fields
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_target_orders INTEGER DEFAULT 360;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_base_salary NUMERIC(12,2) DEFAULT 1500.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_extra_threshold INTEGER DEFAULT 400;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_rate_extra_1 NUMERIC(12,2) DEFAULT 8.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_rate_extra_2 NUMERIC(12,2) DEFAULT 10.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_company_bonus_pct NUMERIC(5,2) DEFAULT 37.5;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_tier_a_bonus NUMERIC(12,2) DEFAULT 100.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_tier_b_penalty NUMERIC(12,2) DEFAULT 300.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_tier_c_penalty NUMERIC(12,2) DEFAULT 500.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_tier_d_penalty NUMERIC(12,2) DEFAULT 1000.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_valid_no_target_rate NUMERIC(12,2) DEFAULT 4.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_invalid_target_rate NUMERIC(12,2) DEFAULT 4.0;
    """)
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS keeta_invalid_no_target_rate NUMERIC(12,2) DEFAULT 2.0;
    """)

    # delivery.contract — service_provider_id
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS service_provider_id INTEGER;
    """)

    _logger.info('delivery_3pl v4.5.0 pre-migration: done.')
