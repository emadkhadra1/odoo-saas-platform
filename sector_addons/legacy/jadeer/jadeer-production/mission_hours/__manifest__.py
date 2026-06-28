{
    "name": "Mission Hours",
    "summary": "Mission Hours",
    # "version": "13.0.0",

    'author': "Archer Solutions",
    'website': "www.archersolutions.com",
    'sequence': 1,
    'category': 'hr',
    'version': '0.1',

    "depends": [
        "hr",
        "hr_holidays",
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/leave_type.xml",
    ],
    'installable': True,
}
