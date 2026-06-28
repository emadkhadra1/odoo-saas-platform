{
    'name': 'Employees Documents Expiry Report',
    'summary': 'Employees Documents Expiry Report',
    'author': 'Archer Solutions',
    'company': 'Archer Solutions',
    'website': "http://www.archersolutions.com",
    'version': '13.0.0.1.0',
    'category': '',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'res_documents',
    ],
    'data': [
        # 'reports/doc_expiry_report.xml',
        # 'wizards/emploee_doc_exp_wiz_view.xml',
        'views/employee_doc_exp_view.xml',
        'views/res_config.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
