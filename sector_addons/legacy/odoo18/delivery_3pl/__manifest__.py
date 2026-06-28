{
    'name': '3PL Delivery Operations Management',
    'version': '18.0.4.6.0',
    'category': 'Operations/Delivery',
    'summary': 'Third-Party Logistics delivery operations for Saudi food delivery platforms',
    'description': """
        3PL Delivery Operations Management System
        ==========================================
        Comprehensive module for managing delivery operations with food delivery platforms
        (Keeta, HungerStation, Jahez, Noon Food, Ninja Food, etc.)

        Features:
        - Company & Branch Management (per city)
        - Versioned Contract Management (per branch) with Parcel/Service types
        - Rider Management (Independent Contractors with fleet vehicle linking)
        - Service Provider Company Management (شركة مزودة خدمة للفرى لانسر)
        - Kafala riders with ID Recipient + prorated Service Provider monthly fee deduction (كفالة + مستلم ID)
        - Rider Advance Payment Tracking (سلفة مقدمة)
        - Rider Archive/Unarchive with platform ID release
        - Advanced Pricing Engine (Per-Order, Per-Distance, Tiered Slabs, Fixed Salary,
          Subcontract Fee, Experience & Capacity Incentives)
        - HungerStation Kafala (كفالة هنقر): Target 550 + Base Salary + Extra per Order
        - Keeta 4-Case Pricing (كيتا): Valid/Invalid × Target/No-Target
        - Fixed Monthly Fee (هنقر فرى / جاهز / توجو)
        - Valid DA Criteria & Experience Score Configuration
        - Daily & Monthly Performance Tracking (color-coded validity)
        - Company Target Management (A/B/C/D levels)
        - Rider Deduction Management (fuel, rent, housing, advance, food, vehicle rental)
        - Fleet Vehicle Linking (company-owned / rented vehicles)
        - Excel Import Engine with Column Mapping
        - Settlement & Multi-stage Approval Workflow with Incentive Breakdown
        - Settlement → Payslip Batch Conversion (hr_payroll integration)
        - Wallet & Penalty Management
        - BI Reports & Dashboards
    """,
    'author': '3PL Solutions',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
        'hr_contract',
        'fleet',
        'hr_payroll',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/delivery_dashboard_views.xml',
        'views/delivery_company_views.xml',
        'views/delivery_branch_views.xml',
        'views/delivery_contract_views.xml',
        'views/delivery_city_views.xml',
        'views/delivery_service_provider_views.xml',
        'views/delivery_rider_views.xml',
        'views/delivery_rider_bulk_import_views.xml',
        'views/delivery_pricing_views.xml',
        'views/delivery_incentive_views.xml',
        'views/delivery_performance_views.xml',
        'views/delivery_target_views.xml',
        'views/delivery_column_map_views.xml',
        'views/delivery_import_views.xml',
        'views/delivery_settlement_views.xml',
        'views/delivery_settlement_batch_wizard_views.xml',
        'views/delivery_penalty_views.xml',
        'views/delivery_wallet_views.xml',
        'views/delivery_hr_contract_views.xml',
        'report/settlement_report.xml',
        'data/delivery_data.xml',
        'data/delivery_payroll_data.xml',
        'data/contracts.xml',
        'views/delivery_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'delivery_3pl/static/src/scss/dashboard.scss',
            'delivery_3pl/static/src/js/dashboard.js',
            'delivery_3pl/static/src/xml/dashboard.xml',
        ],
    },
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 10,
}
