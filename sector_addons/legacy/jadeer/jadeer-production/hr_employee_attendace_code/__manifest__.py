# -*- coding: utf-8 -*-
{
    'name': "Employee Attendance Code",

    'summary': """
        Employee Attendance Code
        """,

    'description': """
        Employee Code used in Attendances Records
    """,

    'author': "Archer Solutions",
    'website': "http://archer.solutions",
    'category': 'HR',
    'version': '13.0.0.1.0',
    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'views/hr_employee.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
