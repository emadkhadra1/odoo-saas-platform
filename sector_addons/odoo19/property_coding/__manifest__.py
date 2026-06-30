# -*- coding: utf-8 -*-
{
    'name': "Property Coding",
    'sequence': 1,

    'summary': """  This module manage coding of units in realestate
          """,

    'description': """
            This module manage coding of units in realestate
        """,

    'author': "Archer Solutions",
    'website': 'www.archer.solutions',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'sale',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'real_estate',
        'project_phase_building_floor'

    ],

    # always loaded
    'data': [
        'views/product.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
