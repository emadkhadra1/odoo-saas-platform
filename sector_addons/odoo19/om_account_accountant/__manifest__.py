{
    "name": "Odoo Mates Accounting Compatibility",
    "version": "19.0.0.0.0",
    "category": "Accounting",
    "summary": "Compatibility shim for construction modules that depend on om_account_accountant.",
    "description": """
Compatibility shim for Odoo 19 demo templates.

This module intentionally provides no accounting features. It satisfies the
technical dependency used by the construction demo modules when the full
Odoo Mates accounting bundle is not available for Odoo 19.
""",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
