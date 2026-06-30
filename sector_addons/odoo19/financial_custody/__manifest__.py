# -*- coding: utf-8 -*-
{
    'name': "Financial Custody",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '19.0.1.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'om_account_accountant', 'analytic', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/custody.xml',
        'views/templates.xml',
        'views/partner.xml',
        'views/employee.xml',
        'data/custody_journal.xml',
        'data/financial_custody_seq.xml',
        'wizard/financial_custody_report_wizard.xml',
        'report/report_financialcustody.xml',
        'report/financial_custody_reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
