# -*- coding: utf-8 -*-
{
    'name': "Customer Care",
    'summary': """Customer Care""",
    'description': """
       Customer Care
    """,
    'author': "Archer",
    'website': "http://www.yourcompany.com",
    'category': 'crm',
    'version': '19.0.1.0.0',
    'depends': [
        'base','real_estate'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'wizard/cancel_reason.xml',
    ],

    'installable': True,
    'auto_install': False,
}
