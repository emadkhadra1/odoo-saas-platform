# -*- coding: utf-8 -*-

{
    'name': 'Archer Cheques Deposit',
    'version': '12',
    'category': 'Accounting & Finance',
    'license': '',
    'summary': 'Manage deposit of Cheques to the bank',
    'author': "Archer Solutions",
    'website': 'http://www.archersolutions.com/',
    'depends': [
        'account',
        'account_accountant',
        'cheque_base',
        'real_estate'
    ],

    'data': [
        'security/check_deposit_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/account_payment_view.xml',
        'views/account_journal.xml',
        'views/check_deposit.xml',
        'wizard/check_cash.xml',
        'wizard/return_cheques_wizard.xml',
        'wizard/return_cheques_to_partner.xml',
        'wizard/collect_wizard.xml',
    ],
    'installable': True,
    'application': True,
}
