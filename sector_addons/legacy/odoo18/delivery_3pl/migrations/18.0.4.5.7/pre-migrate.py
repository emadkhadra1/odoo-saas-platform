from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    v4.5.7 — No schema changes.
    - Fixed monthly performance validity: _auto_create_performance now calls
      _aggregate_from_daily_records() after create/update of monthly records,
      so is_valid and valid_days are computed correctly from daily is_valid_day.
    """
    pass
