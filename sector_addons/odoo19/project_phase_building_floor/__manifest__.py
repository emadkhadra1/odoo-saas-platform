# -*- coding: utf-8 -*-
{
    'name': "project_phase_building_floor",

    'summary': """project_phase_building_floor""",

    'description': """
        phasea_buildinga_floor.
    """,
    'author': "Archer",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'analytic',
        'realestate_project',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/phase.xml',
        'views/building.xml',
        'views/floor.xml',
        'views/menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
