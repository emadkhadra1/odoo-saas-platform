# -*- coding: utf-8 -*-

{
    'name': 'Archer Cheques Base',
    'version': '14',
    'category': 'Accounting & Finance',
    'license': '',
    'summary': 'Archer Cheques Base',
    'author': "Archer Solutions",
    'website': 'http://www.archersolutions.com/',
    'depends': [
        'account',
        'account_accountant',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payment.xml',
    ],
    'installable': True,
    'application': True,
}
