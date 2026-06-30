# -*- coding: utf-8 -*-
##############################################################################
#
#    Constructors, (Constructors).
#
##############################################################################
{
    "name": "قمم - المقاولون وجداول الكميات",

    "version": "19.0.1.0.0",

    "depends": [
        "base",
        "account",
        "om_account_accountant",
        "purchase",
        "project",
        "construction_project",
        'product', 'mail',
        "stock_analytic",
    ],

    'author': "Waell Ahmed.",

    "summary": "You can register all contact in this programs",

    "category": "test",

    "data": [
        "data/data.xml",
        "security/security_groups.xml",
        "security/ir.model.access.csv",

        "wizard/add_bill_lines.xml",

        "views/constructors_view.xml",
        "views/construction_type_view.xml",
        "views/business_item_type_view.xml",
        "views/boq_main_item_view.xml",
        "views/boq_sub_item_view.xml",
        "views/boq_business_item_view.xml",
        "views/boq_sub_business_item_view.xml",
        "views/indexation_view.xml",
        "views/entrepreneurs_view.xml",
        "views/construction_boq_view.xml",
        "views/progress_bill_type_view.xml",
        "views/progress_bill_lines_view.xml",
        "views/progress_bill_view.xml",
        "views/progress_owner_lines_view.xml",
        "views/progress_owner_view.xml",

        "views/deductions_view.xml",
        "views/account_journal_view.xml",
        "views/account_invoice_view.xml",

        "views/b2b_owner_qoutation_report.xml",

        "views/b2b_qoutation_report.xml",
        "views/b2b_qoutation_sum_report.xml",
        "views/b2b_material_sum_report.xml",
        "views/b2b_compare_material_sum_report.xml",

        "views/product_views.xml",
        "views/labour.xml",
        "views/view.xml",
        "views/transportation.xml",

        "wizard/assign_constructor_wizard_view.xml",
        "wizard/quotation_wizard_view.xml",
        "wizard/material_wizard_view.xml",
        "wizard/compare_material_wizard_view.xml",

        "menu.xml",
        "wizard/import_xlsx.xml",
    ],
    "demo": [

    ],

}
