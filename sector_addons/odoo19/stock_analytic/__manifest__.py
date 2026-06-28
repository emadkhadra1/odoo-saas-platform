{
    "name": "Stock Analytic Compatibility",
    "version": "19.0.0.0.0",
    "category": "Inventory",
    "summary": "Compatibility shim for construction modules that depend on stock_analytic.",
    "description": """
Compatibility shim for Odoo 19 demo templates.

This module intentionally provides no stock analytic extensions. It satisfies
the technical dependency used by the construction demo modules when a full
Odoo 19 stock analytic addon is not available.
""",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["stock", "analytic"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
