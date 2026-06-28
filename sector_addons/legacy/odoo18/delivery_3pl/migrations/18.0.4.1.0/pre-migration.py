from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    Drop the old SQL unique constraints on daily and monthly performance tables.
    These are replaced by Python @api.constrains that allow freelancer (sub-rider)
    records sharing the same parent_rider_id to coexist.
    """
    cr.execute("""
        ALTER TABLE delivery_daily_performance
        DROP CONSTRAINT IF EXISTS delivery_daily_performance_unique_rider_date;
    """)
    cr.execute("""
        ALTER TABLE delivery_monthly_performance
        DROP CONSTRAINT IF EXISTS delivery_monthly_performance_unique_rider_month;
    """)
