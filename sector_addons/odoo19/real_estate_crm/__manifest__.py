# -*- coding: utf-8 -*-
{
    'name': "Real Estate CRM",

    'summary': """Real Estate CRM""",

    'description': """
        Real Estate CRM
    """,

    'author': "Archer",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'real_estate',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'crm',
        'sale_crm',
        'real_estate',
        'realestate_project',
        'mail',
        'sale_management',
    ],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/crm_lead.xml',
        'wizards/select_unit.xml',
        'views/data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
