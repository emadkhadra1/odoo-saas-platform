# -*- coding: utf-8 -*-
{
    'name': "TimeOff Customization",

    'summary': """
        TimeOff Customization
        """,
    'description': """
        TimeOff Customization        
    """,

    'author': "Archer Solutions",
    'website': "http://archer.solutions",
    'category': 'hr',
    'version': '15.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr','hr_holidays'
    ],

    # always loaded
    'data': [
        'views/hr_leave.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
