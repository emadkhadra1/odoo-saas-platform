import logging

import psycopg2
from psycopg2 import sql

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
from odoo.tools import config

_logger = logging.getLogger(__name__)


class SaasProvisioningError(Exception):
    """Raised when tenant database provisioning cannot be completed."""


class TenantProvisioningService:
    """Provision tenant databases from a PostgreSQL template database."""

    def __init__(self, env):
        self.env = env

    def provision(self, tenant, admin_password=None):
        tenant.ensure_one()
        template_db = self._get_param("saas_manager.template_database")
        if not template_db:
            raise SaasProvisioningError("Configure a SaaS template database before provisioning tenants.")

        database_created = False
        self._log(tenant, "provision_start", "pending", "Starting tenant provisioning.")
        tenant.action_mark_provisioning()

        try:
            self._create_database_from_template(template_db, tenant.database_name)
            database_created = True
            self._log(tenant, "create_database", "success", "Tenant database was created from template.")

            modules_to_install = self._plan_modules(tenant)
            if modules_to_install:
                self._install_modules(tenant.database_name, modules_to_install)
                self._log(tenant, "install_modules", "success", ", ".join(modules_to_install))

            self._configure_tenant_database(tenant, admin_password=admin_password)
            self._log(tenant, "configure_tenant", "success", "Tenant database settings were applied.")

            tenant.action_activate()
            self._log(tenant, "provision_done", "success", "Tenant provisioning completed.")
            return True
        except Exception as exc:
            _logger.exception("Tenant provisioning failed for %s", tenant.database_name)
            self._log(tenant, "provision_failed", "failed", str(exc), technical_details=repr(exc))
            tenant.action_suspend()
            if database_created:
                self._drop_database_best_effort(tenant.database_name)
            raise

    def suspend_database(self, tenant):
        tenant.ensure_one()
        tenant.action_suspend()
        self._log(tenant, "suspend_tenant", "success", "Tenant was suspended in master database.")

    def reactivate_database(self, tenant):
        tenant.ensure_one()
        tenant.action_activate()
        self._log(tenant, "reactivate_tenant", "success", "Tenant was reactivated in master database.")

    def _get_param(self, key, default=False):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    def _postgres_connection(self):
        db_name = config.get("db_name") or "postgres"
        if "," in db_name:
            db_name = "postgres"
        return psycopg2.connect(
            dbname=db_name,
            user=config.get("db_user") or None,
            password=config.get("db_password") or None,
            host=config.get("db_host") or None,
            port=config.get("db_port") or None,
        )

    def _create_database_from_template(self, template_db, target_db):
        with self._postgres_connection() as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
                if cursor.fetchone():
                    raise SaasProvisioningError("Target database already exists.")
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} WITH TEMPLATE {} OWNER {}").format(
                        sql.Identifier(target_db),
                        sql.Identifier(template_db),
                        sql.Identifier(config.get("db_user") or "odoo"),
                    )
                )

    def _drop_database_best_effort(self, target_db):
        try:
            with self._postgres_connection() as connection:
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT pg_terminate_backend(pid)
                          FROM pg_stat_activity
                         WHERE datname = %s
                           AND pid <> pg_backend_pid()
                        """,
                        (target_db,),
                    )
                    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target_db)))
        except Exception:
            _logger.exception("Rollback database drop failed for %s", target_db)

    def _plan_modules(self, tenant):
        raw_modules = tenant.plan_id.included_modules or ""
        modules = [item.strip() for chunk in raw_modules.splitlines() for item in chunk.split(",")]
        modules.extend(tenant.plan_id.allowed_apps.mapped("name"))
        return sorted({module for module in modules if module})

    def _install_modules(self, db_name, module_names):
        with Registry(db_name).cursor() as cursor:
            env = api.Environment(cursor, SUPERUSER_ID, {})
            modules_to_install = env["ir.module.module"].search([("name", "in", module_names), ("state", "!=", "installed")])
            modules_to_install.button_immediate_install()

    def _configure_tenant_database(self, tenant, admin_password=None):
        with Registry(tenant.database_name).cursor() as cursor:
            env = api.Environment(cursor, SUPERUSER_ID, {})
            params = env["ir.config_parameter"].sudo()
            params.set_param("saas_manager.tenant_uuid", tenant.database_uuid)
            params.set_param("saas_manager.allowed_users", tenant.allowed_users)
            params.set_param("saas_manager.master_database", self.env.cr.dbname)
            company = env.company
            company.name = tenant.company_name
            if tenant.email:
                company.email = tenant.email
            admin = env.ref("base.user_admin", raise_if_not_found=False)
            if admin:
                admin.write(
                    {
                        "name": tenant.contact_name or tenant.company_name,
                        "login": tenant.email,
                        **({"password": admin_password} if admin_password else {}),
                    }
                )
            cursor.commit()

    def _log(self, tenant, action, status, message, technical_details=False):
        self.env["saas.provisioning.log"].sudo().create(
            {
                "tenant_id": tenant.id,
                "action": action,
                "status": status,
                "message": message,
                "technical_details": technical_details,
            }
        )
