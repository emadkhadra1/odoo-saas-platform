{
    "name": "قمم - قواعد الحضور والانصراف",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Attendances",
    "summary": "سياسات سعودية للتأخير والانصراف المبكر والغياب والعمل الإضافي.",
    "author": "Qimam Technical Solutions",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance", "resource", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/attendance_rule_views.xml",
        "views/resource_calendar_views.xml",
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
