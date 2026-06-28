# -*- coding: utf-8 -*-
{
    'name': "Construction Project Modifiction",

    'summary': """Construction Project Mdifiction""",

    'description': """
    """,

    'author': "Zakaria",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','construction_project'],

    # always loaded
    'data': [
        'templates.xml',
      

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}