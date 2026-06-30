# -*- coding: utf-8 -*-
{
    'name': "Partner Custom",
    'summary': """Partner Custom""",
    'description': """
       Partner Custom
    """,
    'author': "Archer",
    'website': "http://www.yourcompany.com",
    'category': 'crm',
    'version': '19.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base','hr','mail'
    ],
    # always loaded
    'data': [
        'views/partner.xml',
        'views/mail_activity.xml',
    ],
    # 'assets':{
    #     'web.assets_qweb': [
    #         'partner_custom/static/src/components/*/*.xml',
    #     ]
    # }

    'installable': True,
    'auto_install': False,
}
