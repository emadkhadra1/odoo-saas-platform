# -*- coding: utf-8 -*-
{
    'name': "Real Estate Security",
    'sequence': 1,
    'summary': """ This module manage realestate access...
          """,
    'description': """ This module manage realestate access.
       """,
    'author': "Archer Solutions",
    'website': 'www.archer.solutions',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'sale',
        'sales_team',
    ],
    'data': [
        'security/realestate_security.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/icon.png'
    ],

}
