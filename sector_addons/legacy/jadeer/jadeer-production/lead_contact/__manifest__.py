# -*- coding: utf-8 -*-
{
    'name': "lead_contact",

    'summary': """lead_contact""",

    'description': """
       lead_contact
    """,
    'author': "Archer",
    'website': "http://www.yourcompany.com",
    'category': 'crm',
    'version': '15.0.1',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm',
        'real_estate_crm'
    ],
    # always loaded
    'data': [
        # 'security/secuirty.xml',
        'security/ir.model.access.csv',
        'views/rec_country.xml',
        'views/crm_lead.xml',
        'wizard/visit.xml',
        'views/crm_lead_to_opportunity_views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
