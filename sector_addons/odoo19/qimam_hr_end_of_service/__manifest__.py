{
    "name": "قمم - نهاية الخدمة",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "دورة تسوية نهاية الخدمة وحساب المستحقات للموظفين في السوق السعودي.",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["hr", "hr_contract", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/end_of_service_sequence.xml",
        "views/end_of_service_views.xml",
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
