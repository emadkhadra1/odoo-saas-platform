# -*- coding: utf-8 -*-
{
    'name': "Real Estate",
    'sequence': 1,

    'summary': """ This module manage realestate full cycle...
          """,

    'description': """ This module manage realestate full cycle.
       """,

    'author': "Archer Solutions",
    'website': 'www.archer.solutions',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_accountant',
        'account_batch_payment',
        'account',
        'crm',
        'sale_management',
        'sale_crm',
        'realestate_project',
        'payment_analytic_account',
        # 'analytic_account_journal_entry',
        'project_phase_building_floor',
        'partner_custom',
        'real_estate_security',
        'web_notify'
        # 'crm_security'
    ],

    # always loaded
    'data': [
        'security/discount_security.xml',
        'security/realestate_security.xml',
        'security/accounting_security.xml',
        'security/ir.model.access.csv',
        'views/account_account.xml',
        # 'views/analytic_account.xml',
        'views/account_invoice.xml',
        'views/crm_lead.xml',
        'views/project_category.xml',
        'views/unit_type.xml',
        'views/attached_area.xml',
        'views/sale_report_templates.xml',
        'views/payment_plan.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/automated_function.xml',
        # 'views/image_preview.xml',
        'views/res_config_settings.xml',
        'views/account_payment.xml',
        'views/account_batch_payment.xml',
        'views/res_partner.xml',
        'views/crm_team.xml',
        'views/crm_lead_to_opportunity.xml',
        'views/privilege.xml',
        'views/utility.xml',
        'views/account_menus.xml',
        # 'views/menus_security.xml',
        'views/project_inherit.xml',
        'views/product_area_building_views.xml',
        'wizard/unit_update.xml',
        'wizard/payment_register_inh.xml',
        'wizard/reserve_request_wizard.xml',
        'wizard/offer_discount_request.xml',
        'data/sequence.xml',
        'views/users.xml',
        'views/project.xml',
        'views/phase.xml',
        'views/utm.xml',
        'views/attach.xml',
        'reports/batch_format.xml',
        'reports/batch_payment.xml',
        'reports/reservation_temp.xml',
        'wizard/update_price_wizard.xml'
    ],
    'images': [
        'static/description/icon.png'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
