{
    'name': "website_portal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','portal','website','ohrms_loan'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/portal_templates.xml',
        'views/leaves.xml',
        # 'views/pr_view.xml',
        # 'views/vendor_registration.xml',
        # 'views/business_trip.xml',
        # 'views/letter_request.xml',
        # 'views/employee_letter_request.xml',
        # 'views/training_request.xml',
        # 'views/salary_request.xml',
        # 'views/bank_request.xml',
        'views/my_profile.xml',
        # 'views/permit_request.xml',
        # 'views/permission_request.xml',
        'views/payslip.xml',
        'views/attendance.xml',
        'views/loan.xml',
        'views/allocations.xml'
        # 'views/portal_reimbursement.xml',
    ],
    # only loaded in demonstration mode
    'assets': {

        'web.assets_frontend': [
            'website_portal/static/css/style.css',
            'website_portal/static/js/toastr/toastr.min.css',
            'website_portal/static/js/toastr/toastr.min.js',
            'website_portal/static/js/jquery-validation/jquery.validate.min.js',
            'website_portal/static/js/jquery-validation/additional-methods.min.js',
            'website_portal/static/flat/flatpickr.min.css',
            'website_portal/static/flat/flatpickr.min.js',
            'website_portal/static/js/custom.js',
            'website_portal/static/js/vendor_reg.js',
            'website_portal/static/js/main.js',
            'website_portal/static/js/mngdp_main.js',
            'website_portal/static/js/leaves.js',
            'website_portal/static/js/loans.js',
            'website_portal/static/js/allocations.js',


        ],
    },
}
# -*- coding: utf-8 -*-
