{
    "name": "Batch Payment Compatibility",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Minimal batch payment compatibility layer for legacy real estate addons.",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["account", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_batch_payment_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
