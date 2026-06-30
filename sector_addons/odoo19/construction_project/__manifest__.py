# -*- coding: utf-8 -*-
{
    'name': "قمم - مشاريع المقاولات",

    'summary': """
       Construction Project """,

    'description': """
       Construction Project
    """,

    'author': "Hashem ALY Smart.hashem@gmail.com",
    'website': "mailto:smart.hashem@gmail.com",

    'category': 'sale',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'account', 'om_account_accountant', 'purchase_requisition', 'stock', 'product',
                'sale_management', 'stock_analytic', 'company_modifications'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/construction_project.xml',
        'views/construction_unit.xml',
        'views/construction_item.xml',
        'views/construction_component.xml',
        'views/construction_receive_order.xml',
        # 'views/construction_service.xml',
        'views/construction_labor.xml',
        'views/construction_machine.xml',
        'views/construction_tool.xml',
        'views/construction_contract_type.xml',
        'views/construction_project_dashboard.xml',
        'views/view_menus.xml',
        'views/stock_quant.xml',
        'views/account_move.xml',
        'reports/print_receive_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}
