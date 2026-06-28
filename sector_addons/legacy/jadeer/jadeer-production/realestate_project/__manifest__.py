# -*- coding: utf-8 -*-
{
    'name': "RealEstate Project",
    'sequence': 1,

    'summary': """  This module manage coding of units in realestate.
          """,
    'description': """
            This module manage coding of units in realestate
        """,
    'author': "Archer Solutions",
    'website': 'www.archer.solutions',
    'category': 'sale',
    'version': '0.1',

    'depends': [
        'base',
        'sale',
        'product',
        'account_accountant',
        'account',
        'crm',
        'sale_management',
        'sale_crm',
        'account_budget',
        'real_estate_security',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_project.xml',
        'views/project.xml',
        'views/image_preview.xml',

    ],

}
