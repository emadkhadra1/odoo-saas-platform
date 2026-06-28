# Odoo SaaS Platform

Multi-database Odoo SaaS management platform with an interactive marketing website.

## Addons

### `odoo_saas_manager`

Install in the **Master Database** to manage:

- Tenants and isolated databases
- SaaS plans
- Subscriptions and payments
- Provisioning logs
- User limits
- Onboarding imports
- Token-protected API endpoints

### `odoo_saas_website`

Install in the database hosting the public Odoo Website.

Public presentation URL:

```text
/saas-platform
```

The website includes sector features, Saudi Riyal prices, and an interactive SaaS backend preview.

Sector demo database setup:

```text
docs/sector_demo_databases.md
```

Server deployment helper:

```bash
bash deployment/deploy_addons_to_docker.sh
```

## Standalone Previews

- `outputs/marketing_site/`
- `outputs/demo_hub/`

## Version Notes

- SaaS Manager and Website bridge target Odoo 19.
- 3PL source targets Odoo 18.
- Construction source targets Odoo 19.
- Legacy Real Estate and Saudi HR sources require compatibility review before production deployment.

## Security

Never commit database dumps, filestores, `.env` files, SSH keys, API tokens, or production credentials.
