from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    v4.5.6 — No schema changes.
    - Fixed _auto_create_performance branch resolution:
      Priority: session.branch > contract.branch > sole company branch > rider.branch
    """
    pass
