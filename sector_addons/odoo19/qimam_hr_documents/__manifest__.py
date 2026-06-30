{
    "name": "قمم - وثائق الموظفين",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "متابعة وثائق الموظفين ومواعيد الانتهاء والمرفقات مثل الإقامة والجواز والعقود.",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/document_types.xml",
        "views/hr_document_views.xml",
        "views/hr_employee_views.xml",
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
