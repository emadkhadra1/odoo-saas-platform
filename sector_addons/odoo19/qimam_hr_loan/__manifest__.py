{
    "name": "قمم - السلف والقروض",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "طلبات السلف والقروض واستقطاع الأقساط للموظفين وفق احتياج السوق السعودي.",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["hr", "hr_contract", "hr_payroll", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/loan_sequence.xml",
        "views/hr_loan_views.xml",
        "views/hr_employee_views.xml",
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
