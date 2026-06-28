
{
    'name': 'Employee Penalty',
    'summary': 'Employee Penalty',
    'author': 'Archer Solutions',
    'company': 'Archer Solutions',
    'website': "http://www.archersolutions.com",
    'version': '15.0.0.1.0',
    'category': 'HR',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'hr',
        'hr_payroll','hr_work_entry_contract_enterprise',
        'contract_work_hour'
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/employee_penalty.xml',
        'views/hr_payslip.xml',
        'views/menu.xml',
        'data/data.xml',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'auto_install': False,
}

