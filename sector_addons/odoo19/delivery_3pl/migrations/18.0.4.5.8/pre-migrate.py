from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    v4.5.8 — No schema changes.
    - Fixed _aggregate_from_daily_records: when no daily records exist,
      uses stored valid_days to compute is_valid (instead of resetting to 0).
    - Fixed monthly import path: computes and stores is_valid immediately
      from imported valid_days using validity criteria.
    """
    pass
