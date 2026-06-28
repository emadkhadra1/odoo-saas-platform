
{
    'name': 'Extra Approve For Time Off',
    'summary': 'Extra Approve For Time Off',
    'author': 'Archer Solutions',
    'company': 'Archer Solutions',
    'website': "http://www.archersolutions.com",
    'version': '13.0.0.1.0',
    'category': '',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'hr',
        'hr_holidays',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_employee.xml',
        'views/hr_leave.xml',
        'views/hr_leave_type.xml',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

