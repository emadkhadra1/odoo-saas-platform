# -*- coding: utf-8 -*-

{
    'name': 'Archer Cheques Deposit Custom',
    'version': '12',
    'category': 'Accounting & Finance',
    'license': '',
    'summary': 'Archer Cheques Deposit Custom',
    'author': "Archer Solutions",
    'website': 'http://www.archersolutions.com/',
    'depends': [
        'account',
        'cheque_deposit',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/check_deposit.xml',
        'wizard/check_transfer.xml',
    ],
    'installable': True,
    'application': True,
}
