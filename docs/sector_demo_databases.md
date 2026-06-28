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
- 3PL module: original archive shows `18.0.4.6.0`; an initial Odoo 19 copy now exists at `sector_addons/odoo19/delivery_3pl` with manifest `19.0.4.6.0`, but it still needs an install test on the Odoo 19 server.
- Saudi HR archive: currently provided as `.rar`; extract it or send it as `.zip` so manifests can be inspected.
- Real estate archive: inspected `jadeer-production.zip`; manifests are mostly Odoo 12 to 15 and some modules have no reliable version, so it needs an Odoo 19 conversion before it is safe as a production template.
