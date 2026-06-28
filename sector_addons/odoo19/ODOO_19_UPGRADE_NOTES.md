# Odoo 19 Upgrade Notes

This package was updated for Odoo Community 19 compatibility and for use with
`om_account_accountant`.

Main changes:

- Updated addon manifest versions to `19.0.1.0.0`.
- Added `om_account_accountant` dependency to accounting-related addons.
- Converted XML list views from legacy `<tree>` tags to Odoo 19 `<list>` tags.
- Updated action `view_mode` values from `tree` to `list`.
- Replaced legacy XML `colors` list styling with decoration attributes.
- Replaced deprecated Python field option `track_visibility` with `tracking=True`.
- Replaced invoice residual usage with `amount_residual`.
- Replaced old journal-line `analytic_account_id` values with `analytic_distribution`.
- Removed old `decimal_precision` imports and kept custom precision usage through
  `digits='Constructor price'`.

Validation performed:

- Python compile check over all addons.
- XML parse check over all XML files.

Install notes:

- Install or place `om_account_accountant` in the Odoo addons path before
  installing these modules.
- Keep any external dependencies already required by the original package, such
  as `stock_analytic`, `purchase_requisition`, and `hr_employee_updation`, in
  the addons path if you install modules that depend on them.
