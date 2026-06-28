from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    v4.5.4 migrations:
    1. Add rider_type column to delivery.contract (default='all')
    2. Bug fix: _auto_create_performance branch fallback (no schema change — carried from v4.5.3)
    3. action_reactivate for terminated/expired contracts (no schema change)
    """
    cr.execute("""
        ALTER TABLE delivery_contract
        ADD COLUMN IF NOT EXISTS rider_type VARCHAR DEFAULT 'all';
    """)
    cr.execute("""
        UPDATE delivery_contract
        SET rider_type = 'all'
        WHERE rider_type IS NULL;
    """)
