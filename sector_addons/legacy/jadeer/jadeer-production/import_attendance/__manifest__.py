# -*- coding: utf-8 -*-
{
    'name': 'Import Attendances',
    'summary': "Import Attendances from CSV/Excel",
    'description': "General Import Attendances from CSV/Excel",

    'author': "Archer Solutions",
    'website': "http://archer.solutions",

    'category': 'Attendance',
    'version': '13.0.0.1.0',
    'depends': [
        'hr_attendance',
        'hr_employee_attendace_code',
        'attendances_structure_base',
        'attendance_rules'
    ],
    'external_dependencies': {
        'python': [
            'xlrd',
            'xlwt',
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_attendance_view.xml',
        'views/attendance_records.xml',
        'views/res_config_setting.xml',
    ],

    'auto_install': False,
    'installable': True,

}
