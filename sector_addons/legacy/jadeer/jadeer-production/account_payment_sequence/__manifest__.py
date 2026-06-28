# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Sequence',
    'version': '12',
    'category': 'Accounting & Finance',
    'license': '',
    'summary': 'Account Payment Sequence',
    'author': "Archer Solutions",
    'website': 'http://www.archersolutions.com/',
    'depends': [
        'account_accountant','account',
    ],
    'data': [
        'views/account_journal.xml',
        'views/check_payment.xml',
        'views/account_bank_statement.xml',

    ],
    'installable': True,
    'application': True,
}
