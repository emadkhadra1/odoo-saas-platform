# Odoo SaaS Manager

`odoo_saas_manager` is an Odoo Community addon for managing a real multi-database SaaS operation from a master database. The master database stores tenants, plans, subscriptions, payments, and provisioning logs. Each customer is intended to run in an isolated tenant database created from a controlled template database.

## Phase 1 Architecture

The current workspace was empty, so this addon starts as a standalone Odoo module.

Recommended production architecture:

1. **Master database**
   - Install `odoo_saas_manager` only in the master database.
   - Store commercial and operational data: tenants, plans, subscriptions, payments, provisioning logs, API tokens, onboarding imports, and dashboard metrics.
   - Do not store tenant business records in the master database.

2. **Tenant databases**
   - Create one PostgreSQL/Odoo database per customer.
   - Use a hardened template database with the base SaaS runtime, shared theme/configuration, and required vertical modules.
   - Install extra modules according to the tenant plan after database creation.

3. **Tenant isolation**
   - Isolation boundary is the PostgreSQL database, not only Odoo multi-company.
   - Tenant users authenticate only against their own database.
   - Master database users manage SaaS operations and should not use tenant databases for daily tenant work.

4. **Provisioning flow for Phase 3**
   - Validate tenant subdomain and database name.
   - Create a provisioning log record.
   - Use PostgreSQL/Odoo APIs where possible, not shell commands.
   - Clone from a template database.
   - Open an Odoo registry for the new database.
   - Install modules from the selected plan.
   - Create the tenant admin user.
   - Configure company data and tenant limits.
   - Mark tenant active or roll back and mark failed/suspended.

5. **Domain routing**
   - Reserve a wildcard DNS record such as `*.mycompany.com`.
   - Route requests through a reverse proxy to Odoo.
   - Map `client1.mycompany.com` to the tenant database name stored in `saas.tenant.database_name`.
   - Keep the master database on a separate hostname such as `saas-admin.mycompany.com`.

Suggested commit message for Phase 1:

```text
docs: define multi-database SaaS architecture for Odoo manager
```

## Phase 2 Core Models

Implemented models:

- `saas.tenant`
- `saas.plan`
- `saas.subscription`
- `saas.payment`
- `saas.provisioning.log`

Included module assets:

- Manifest and Python model registration.
- Security groups: SaaS Admin, SaaS Manager, SaaS Accountant, SaaS Support.
- Access rights and record rules so ordinary users do not see SaaS records unless assigned to SaaS groups.
- Tenant, plan, subscription, payment, and provisioning log views.
- SaaS Manager menu.
- Tenant sequence.
- Demo SaaS plans.
- Basic TransactionCase tests.

Suggested commit message for Phase 2:

```text
feat: add core SaaS tenant billing models and admin views
```

Demo data now includes vertical SaaS plans mapped to the provided sector modules:

- `CONSTRUCTION_BUSINESS`
- `THREE_PL_BUSINESS`
- `REAL_ESTATE_BUSINESS`
- `SAUDI_HR_BUSINESS`

## Installation

1. Copy `odoo_saas_manager` into an Odoo addons path.
2. Update the Odoo app list.
3. Install **Odoo SaaS Manager** in the master database.
4. Assign users to one of the SaaS groups.

Example Odoo command:

```bash
odoo-bin -d master_db -i odoo_saas_manager --addons-path=/path/to/addons
```

## Next Phases

## Phase 3 Provisioning

Implemented foundation:

- `services/provisioning_service.py`
- Tenant button action to provision from the configured template database.
- PostgreSQL database creation through `psycopg2` and safe `sql.Identifier` usage.
- Module installation from `saas.plan.included_modules` and `saas.plan.allowed_apps`.
- Tenant admin and company setup.
- Best-effort rollback by dropping the newly created database if provisioning fails.
- Step-by-step `saas.provisioning.log` records.

Required setting:

- `saas_manager.template_database`

Suggested commit message:

```text
feat: add tenant provisioning service from template database
```

## Phase 4 Billing

Implemented:

- Daily cron `SaaS: Check Subscriptions`.
- Trial expiry handling.
- Billing-date checks.
- Automatic draft customer invoice creation when Accounting is installed.
- Manual payment records with `Mark Paid` and `Mark Failed` actions.
- Gateway-ready abstraction point through `saas.payment.transaction_reference` and API payment recording.

Suggested commit message:

```text
feat: add subscription billing cron and manual payment flow
```

## Phase 5 User Limits

Implemented:

- `res.users` guard that reads `saas_manager.allowed_users`.
- User creation/reactivation is blocked when the active internal user limit is exceeded.
- `res.users.saas_get_active_users_count()` for master synchronization.
- `saas.tenant.sync_active_users_count()` opens the tenant registry and refreshes `active_users_count`.

Install this addon in each tenant database, or extract the `res.users` extension into a smaller tenant-agent addon for stricter separation.

Suggested commit message:

```text
feat: enforce tenant active user limits
```

## Phase 6 Dashboard

Implemented:

- `saas.dashboard` transient model.
- Dashboard menu with:
  - Active tenants
  - Expired subscriptions
  - MRR
  - ARR
  - Suspended tenants
  - Trial tenants

Suggested commit message:

```text
feat: add SaaS management dashboard metrics
```

## Phase 7 Security

Implemented:

- SaaS Admin
- SaaS Manager
- SaaS Accountant
- SaaS Support
- Access rights for every persistent model plus dashboard/import wizard.
- Record rules scoped to SaaS groups so normal users do not see SaaS records.

Suggested commit message:

```text
chore: add SaaS role-based access controls
```

## Phase 8 API

Set `saas_manager.api_key` in Settings before using the API.

JSON endpoints:

- `/saas/api/tenant/create`
- `/saas/api/tenant/status`
- `/saas/api/tenant/suspend`
- `/saas/api/tenant/reactivate`
- `/saas/api/tenant/change-plan`
- `/saas/api/payment/record`
- `/saas/api/subscription/details`

Example JSON payload:

```json
{
  "token": "secret",
  "tenant_id": 1
}
```

Suggested commit message:

```text
feat: add token-protected SaaS JSON API
```

## Phase 9 Onboarding Import

Implemented wizard:

- Upload CSV/XLSX in master database.
- Select tenant.
- Select data type:
  - Employees
  - Properties
  - Projects
  - Students
  - Customers
- Validate required columns.
- Open tenant database and create records in the target model when installed.
- Log import result.

Suggested commit message:

```text
feat: add tenant onboarding import wizard
```

## Phase 10 Code Quality

Implemented:

- Modular models, services, controllers, and wizards.
- Docstrings on key classes/methods.
- Logging and explicit error handling in provisioning/import flows.
- Demo plan data.
- Basic TransactionCase tests.
- README install and architecture documentation.

Suggested commit message:

```text
test: cover core SaaS model behavior and dashboard metrics
```
