{
    'name': 'Qimam Backend Theme',
    'version': '19.0.1.1.0',
    'category': 'Themes/Backend',
    'summary': 'Qimam visual identity for Odoo backend and login screens',
    'description': """
Qimam Backend Theme
===================
Applies Qimam Technical Solutions visual identity to Odoo backend screens
without modifying Odoo core files.
    """,
    'author': 'Qimam Technical Solutions',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'qimam_backend_theme/static/src/scss/backend.scss',
            'qimam_backend_theme/static/src/js/app_launcher.js',
        ],
        'web.assets_frontend': [
            'qimam_backend_theme/static/src/scss/login.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 1,
}
