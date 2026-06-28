# -*- coding: utf-8 -*-

{
    'name': 'Archer Cheques Issuance',
    'version': '12',
    'category': 'Accounting & Finance',
    'license': '',
    'summary': 'Manage Issuance of Cheques to the bank',
    'author': "Archer Solutions",
    'website': 'http://www.archersolutions.com/',
    'depends': [
        'account',
        'account_accountant',
        'cheque_base',
        'cheque_deposit',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/account_payment.xml',
        'views/partner.xml',
    ],
    'installable': True,
    'application': True,
}
