# -*- coding: utf-8 -*-
{
    'name': "Construction Project Reports",

    'summary': """Construction Project Reports""",

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
        'reports/total_cost_report.xml',
        'reports/total_detialed_cost_report.xml',
        'reports/receive_order_report.xml',
        'reports/labor_order_report.xml',
        'reports/machine_order_report.xml',
        'reports/tool_order_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}