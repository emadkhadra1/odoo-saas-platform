def migrate(cr, version):
    """Add pricing_mode and rider_monthly_fee columns to delivery_contract."""
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS pricing_mode VARCHAR DEFAULT 'standard',
        ADD COLUMN IF NOT EXISTS rider_monthly_fee NUMERIC(12,2) DEFAULT 0.0
    """)
