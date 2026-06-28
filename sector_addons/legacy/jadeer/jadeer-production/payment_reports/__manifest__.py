# -*- coding: utf-8 -*-
{
    'name': "Payment Reports",

    'summary': """Payment Reports""",

    'description': """
    """,
    'author': "Archer",
    'category': 'account',
    'version': '15.0.1',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_accountant',
        'account_batch_payment'
    ],
    # always loaded
    'data': [
        'reports/paperformat.xml',
        'reports/send_payment_report.xml',
        'reports/receive_payment.xml',
        'views/jounral.xml'
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
