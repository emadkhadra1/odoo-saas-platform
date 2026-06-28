from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    v4.5.5 — No schema changes.
    - Added ToYou VDA column aliases: Online Day, Sum of total delivered tasks,
      Sum of on time D tasks, Cancellation(D), Total Delivery Distance (km)
    - Added action_cancel_and_re_upload on import session
    """
    pass
