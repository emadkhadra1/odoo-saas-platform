# -*- coding: utf-8 -*-
{
    'name': "Hr Employee Customization",

    'summary': """
        Hr Employee Customization
        """,
    'description': """
        Hr Employee Customization        
    """,

    'author': "Archer Solutions",
    'website': "http://archer.solutions",
    'category': 'hr',
    'version': '15.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr','hr_payroll'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/payslip_report.xml',
        'views/update_emp_info.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
