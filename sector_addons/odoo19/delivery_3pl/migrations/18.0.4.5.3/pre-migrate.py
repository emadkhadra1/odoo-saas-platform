from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    v4.5.3 — Bug fix: no schema changes.
    _auto_create_performance now uses each rider's branch as fallback
    when the import session has no branch_id set.
    """
    pass
