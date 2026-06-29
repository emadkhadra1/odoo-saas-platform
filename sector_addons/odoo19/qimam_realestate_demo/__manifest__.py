{
    "name": "Qimam Real Estate Demo",
    "version": "19.0.1.0.0",
    "category": "Real Estate",
    "summary": "Odoo 19 real estate demo for projects, units, reservations, and payment plans.",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/realestate_views.xml",
        "data/realestate_demo_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
