# Compatibility Matrix

هذه المصفوفة تحدد كيف نتعامل مع كل قطاع قبل تحويله إلى ديمو SaaS قابل للبيع.

## Summary

| Sector | Source | Detected Version | Status | Recommended Demo Path |
|---|---:|---:|---|---|
| 3PL / Delivery | `delivery_3pl_v4.6.0.zip` | Odoo 18 | Strong candidate | Build Odoo 18 demo tenant first |
| Construction | `emad_construction_odoo19_modules_ready.zip` | Odoo 19 | Strong candidate | Build Odoo 19 demo tenant or port manager to 19 |
| Real Estate | `jadeer-production.zip` | Mixed, likely Odoo 15/legacy | Needs upgrade review | Start with module inventory and install chain cleanup |
| Saudi HR | `saudi hr.rar` | Odoo 15-era HR stack | Needs upgrade review | Build legacy demo first, then plan upgrade |
| Education | `edusaas-project-source.tar.gz` | React/API, not Odoo addon | External portal | Use as website/app demo integrated with SaaS API |

## Key Risks

1. **Different Odoo versions**
   - 3PL targets Odoo 18.
   - Construction targets Odoo 19.
   - Jadeer and Saudi HR appear older and may require migration.

2. **Enterprise/community dependencies**
   - Some modules reference `account_accountant`, `hr_payroll`, and `account_batch_payment`.
   - On Odoo Community, replacements or compatibility modules may be required.

3. **Third-party dependencies**
   - Construction references `om_account_accountant` and `stock_analytic`.
   - Real Estate references several custom Jadeer modules.
   - HR references Open HRMS-style dependencies such as `hr_employee_updation`.

4. **Education is not Odoo-native yet**
   - It should be shown as an external portal in the first demo.
   - Later it can become either Odoo website/portal pages or native LMS addons.

## Recommended Environments

### Master SaaS Environment

```text
Odoo 18 or 19
Database: master_saas
Installed:
- odoo_saas_manager
- website
- crm
- account
```

### Demo Tenant Environments

```text
tenant_3pl_demo          -> Odoo 18
tenant_construction_demo -> Odoo 19
tenant_realestate_demo   -> legacy-compatible environment first
tenant_hr_demo           -> legacy-compatible environment first
tenant_edu_demo          -> Odoo portal + external EduSaaS app
```

## Decision

Do not force all sectors into one database for the demos. Use separate tenant demo databases so each sector can run on the safest Odoo version while the master SaaS layer presents them as one product suite.
