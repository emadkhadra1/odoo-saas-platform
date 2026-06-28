# -*- coding: utf-8 -*-
{
    'name': 'Open HRMS Loan Management Custom',
    'version': '13.0.1.1.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'hr',
    'author': "Archer Solutions",
    'company': 'Archer Solutions',
    'maintainer': 'Archer Solutions',
    'website': "",
    'depends': [
        'base',
        'hr_payroll',
        'hr',
        'account',
        'ohrms_loan',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/loan.xml',
        'views/ohrm_type.xml',
        'views/loan_rescudule.xml'
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
