{
    "name": "HR Contract Compatibility",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Minimal HR contract model for sector demo modules.",
    "license": "LGPL-3",
    "depends": ["hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_contract_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
