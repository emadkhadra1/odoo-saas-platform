# -*- coding: utf-8 -*-

{
    'name': 'Attendance Rules',
    'version': '13.0.0',
    'summary': """Attendance Rules""",
    'description': """Attendance Rules""",
    'category': 'Attendances',
    'author': 'Archer Solutions',
    'company': 'Archer Solutions',
    'website': "http://www.archersolutions.com",
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'resource',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendances_rules.xml',
        'views/resource_calendar.xml',
    ],
    'demo': [''],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
