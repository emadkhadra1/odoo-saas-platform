# -*- coding: utf-8 -*-
{
    'name': 'Social Insurence',
    'version': '12.0.1.0.0',
    'category': 'Hr',
    'author': "Archer Solutions",
    'website': "www.archersolutions.com",
    'summary': 'this app manage social insurence of employees',
    'sequence': 1,
    'depends': [
        'base', 'hr', 'hr_payroll', 'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/social_insurence.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/retirement_percentage.xml',
        'views/payslip.xml',
        'views/res_config_setting.xml',
        'wizard/insurance_wizard.xml',
        'wizard/report.xml'
    ],
    'installable': True,
}
