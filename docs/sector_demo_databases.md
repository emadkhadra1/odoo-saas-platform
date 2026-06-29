# Sector Demo Databases

This platform uses one Odoo master database plus isolated tenant databases.

## Database Roles

| Role | Database name | Purpose |
| --- | --- | --- |
| Master | `sass` | SaaS Manager, website, CRM leads, plans, subscriptions |
| Construction template | `tenant_template_construction` | Clean sector template used for new construction tenants |
| Real estate template | `tenant_template_realestate` | Clean sector template used for new real estate tenants |
| Saudi HR template | `tenant_template_saudi_hr` | Clean sector template used for new HR tenants |
| 3PL template | `tenant_template_3pl` | Clean sector template used for new 3PL tenants |
| Construction public demo | `demo_construction` | Website "Try Demo" target |
| Real estate public demo | `demo_realestate` | Website "Try Demo" target |
| Saudi HR public demo | `demo_hr` | Website "Try Demo" target |
| 3PL public demo | `demo_3pl` | Website "Try Demo" target |

## Website Demo Routes

The public website routes are:

```text
/demo/construction
/demo/real-estate
/demo/hr
/demo/3pl
```

Each route redirects to `/web/login?db=<demo_database>`.

The database names can be changed from Odoo system parameters:

```text
qimam_saas_website.demo_database_construction
qimam_saas_website.demo_database_real_estate
qimam_saas_website.demo_database_hr
qimam_saas_website.demo_database_3pl
```

## SaaS Plan Templates

The sector plans in SaaS Manager already point to these template databases:

```text
Construction Business -> tenant_template_construction
Real Estate Business  -> tenant_template_realestate
Saudi HR Business     -> tenant_template_saudi_hr
3PL Business          -> tenant_template_3pl
```

When a paid customer subscribes, create a tenant in SaaS Manager, select the sector plan, set a database name such as `tenant_acme_construction`, then click **Provision**. SaaS Manager clones the selected template database into the customer database.

## Server Commands

Run these commands on the Hetzner server.

### Phase 1: Pull and deploy addons

```bash
cd /opt/odoo/custom-addons/odoo-saas-platform
git pull origin main
bash deployment/deploy_addons_to_docker.sh
```

Upgrade the SaaS manager and website in the master database:

```bash
docker exec -it odoo19 odoo -d sass -u odoo_saas_manager,odoo_saas_website --stop-after-init
docker restart odoo19
```

### Phase 2: Bootstrap the construction demo

The construction template can be created from the Odoo 19 construction addons once all required dependencies are available inside the Odoo container.

```bash
cd /opt/odoo/custom-addons/odoo-saas-platform
PUBLIC_BASE_URL=http://178.104.83.32:8069 RESET_TEMPLATE=1 bash deployment/bootstrap_sector_demo.sh construction
```

The script will:

- copy this repository's addons into `odoo19:/mnt/extra-addons`
- check that required dependencies exist
- create or upgrade `tenant_template_construction`
- clone it into `demo_construction`
- print the demo login URL

If it stops with missing dependencies such as `om_account_accountant` or `stock_analytic`, copy those Odoo 19 addons into `/mnt/extra-addons` or add their path through `ADDONS_PATHS`, then rerun the same command.

### Phase 3: Check demo readiness

```bash
PUBLIC_BASE_URL=http://178.104.83.32:8069 bash deployment/check_demo_databases.sh
```

The expected first ready demo route is:

```text
http://178.104.83.32:8069/demo/construction
```

That route redirects to:

```text
http://178.104.83.32:8069/web/login?db=demo_construction
```

### Phase 4: Refresh public demo copies

After a template is prepared, refresh its public demo database:

```bash
bash deployment/create_demo_databases.sh
```

This clones every template that exists and skips templates that are not ready yet.

### Manual database commands

List existing databases:

```bash
docker exec -it odoo19-db psql -U odoo -d postgres -c "SELECT datname FROM pg_database ORDER BY datname;"
```

Clone a public demo database from a prepared template:

```bash
docker exec -it odoo19-db psql -U odoo -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'demo_construction';"
docker exec -it odoo19-db dropdb -U odoo --if-exists demo_construction
docker exec -it odoo19-db createdb -U odoo -T tenant_template_construction demo_construction
```

Repeat for the other sectors:

```bash
docker exec -it odoo19-db dropdb -U odoo --if-exists demo_realestate
docker exec -it odoo19-db createdb -U odoo -T tenant_template_realestate demo_realestate

docker exec -it odoo19-db dropdb -U odoo --if-exists demo_hr
docker exec -it odoo19-db createdb -U odoo -T tenant_template_saudi_hr demo_hr

docker exec -it odoo19-db dropdb -U odoo --if-exists demo_3pl
docker exec -it odoo19-db createdb -U odoo -T tenant_template_3pl demo_3pl
```

If PostgreSQL says the source database is being used, terminate sessions first:

```bash
docker exec -it odoo19-db psql -U odoo -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('tenant_template_construction','tenant_template_realestate','tenant_template_saudi_hr','tenant_template_3pl','demo_construction','demo_realestate','demo_hr','demo_3pl') AND pid <> pg_backend_pid();"
```

Set demo login credentials inside each demo database from Odoo UI or Odoo shell. Do not commit real demo passwords to Git.

## Compatibility Status

- SaaS Manager: Odoo 19.
- Marketing website: Odoo 19.
- Construction modules: manifests show `19.0.1.0.0`.
- Construction includes Odoo 19 compatibility shims for `om_account_accountant` and `stock_analytic` so demo templates can be installed. Replace them with full production-grade Odoo 19 addons if those accounting or inventory analytic features are required.
- 3PL module: Odoo 19 demo template is available through `tenant_template_3pl` and public demo database `demo_3pl`.
- Saudi HR demo: Odoo 19 demo template is available through `tenant_template_saudi_hr` using `hr_contract`, `hr_payroll`, and `qimam_hr_demo`. The larger Saudi HR custody/loans/attendance stack is still legacy/incomplete and should be migrated separately before production use.
- Real estate demo: Odoo 19 demo template is available through `tenant_template_realestate` using `qimam_realestate_demo` for projects, units, reservations, and payment plans. The full Jadeer legacy real estate stack still needs a separate Odoo 19 migration before production use.
