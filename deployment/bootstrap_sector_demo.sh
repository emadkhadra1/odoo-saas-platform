#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash deployment/bootstrap_sector_demo.sh construction
  bash deployment/bootstrap_sector_demo.sh 3pl
  bash deployment/bootstrap_sector_demo.sh hr

Environment variables:
  ODOO_CONTAINER=odoo19
  POSTGRES_CONTAINER=odoo19-db
  POSTGRES_USER=odoo
  ODOO_BIN=odoo
  ODOO_CONFIG=/etc/odoo/odoo.conf
  ODOO_DB_HOST=<auto from Odoo container HOST env>
  ODOO_DB_PORT=5432
  ODOO_DB_USER=<auto from Odoo container USER env>
  ODOO_DB_PASSWORD=<auto from Odoo container PASSWORD env>
  ADDONS_PATHS="/mnt/extra-addons /usr/lib/python3/dist-packages/odoo/addons /var/lib/odoo/addons/19.0"
  DEPLOY_ADDONS=1
  RESET_TEMPLATE=0
  CLONE_DEMO=1
  PUBLIC_BASE_URL=http://127.0.0.1:8069
USAGE
}

SECTOR="${1:-}"
if [ -z "${SECTOR}" ] || [ "${SECTOR}" = "-h" ] || [ "${SECTOR}" = "--help" ]; then
  usage
  exit 0
fi

ODOO_CONTAINER="${ODOO_CONTAINER:-odoo19}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-odoo19-db}"
POSTGRES_USER="${POSTGRES_USER:-odoo}"
ODOO_BIN="${ODOO_BIN:-odoo}"
ODOO_CONFIG="${ODOO_CONFIG:-/etc/odoo/odoo.conf}"
ADDONS_PATHS="${ADDONS_PATHS:-/mnt/extra-addons /usr/lib/python3/dist-packages/odoo/addons /var/lib/odoo/addons/19.0}"
DEPLOY_ADDONS="${DEPLOY_ADDONS:-1}"
RESET_TEMPLATE="${RESET_TEMPLATE:-0}"
CLONE_DEMO="${CLONE_DEMO:-1}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://127.0.0.1:8069}"

case "${SECTOR}" in
  construction)
    TEMPLATE_DB="tenant_template_construction"
    DEMO_DB="demo_construction"
    INSTALL_MODULES="account,project,purchase,stock,sale_management,mrp,company_modifications,construction_project,b2b_constructors,b2b_constructor_edit,construction_budgeting,construction_project_modifiction,construction_project_reports,financial_custody"
    REQUIRED_ADDONS=(
      base mail web account analytic project purchase purchase_requisition stock stock_analytic product sale_management mrp hr
      om_account_accountant company_modifications construction_project b2b_constructors b2b_constructor_edit
      construction_budgeting construction_project_modifiction construction_project_reports financial_custody
    )
    ;;
  3pl|delivery_3pl)
    TEMPLATE_DB="tenant_template_3pl"
    DEMO_DB="demo_3pl"
    INSTALL_MODULES="hr_contract,fleet,delivery_3pl"
    REQUIRED_ADDONS=(base mail web hr hr_contract fleet hr_payroll delivery_3pl)
    ;;
  real-estate|realestate|real_estate)
    TEMPLATE_DB="tenant_template_realestate"
    DEMO_DB="demo_realestate"
    INSTALL_MODULES="qimam_realestate_demo"
    REQUIRED_ADDONS=(base mail web qimam_realestate_demo)
    ;;
  hr|saudi_hr|saudi-hr)
    TEMPLATE_DB="tenant_template_saudi_hr"
    DEMO_DB="demo_hr"
    INSTALL_MODULES="hr_contract,hr_payroll,qimam_hr_demo"
    REQUIRED_ADDONS=(base mail web hr hr_contract hr_payroll qimam_hr_demo)
    ;;
  *)
    echo "Unknown sector: ${SECTOR}" >&2
    usage >&2
    exit 2
    ;;
esac

container_exists() {
  docker ps --format '{{.Names}}' | grep -Fxq "$1"
}

require_containers() {
  if ! container_exists "${ODOO_CONTAINER}"; then
    echo "Odoo container is not running: ${ODOO_CONTAINER}" >&2
    exit 1
  fi
  if ! container_exists "${POSTGRES_CONTAINER}"; then
    echo "PostgreSQL container is not running: ${POSTGRES_CONTAINER}" >&2
    exit 1
  fi
}

container_env() {
  local key="$1"
  docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "${ODOO_CONTAINER}" \
    | awk -F= -v wanted="${key}" '$1 == wanted {print substr($0, length(wanted) + 2); exit}'
}

load_odoo_db_args() {
  ODOO_DB_HOST="${ODOO_DB_HOST:-$(container_env HOST)}"
  ODOO_DB_PORT="${ODOO_DB_PORT:-5432}"
  ODOO_DB_USER="${ODOO_DB_USER:-$(container_env USER)}"
  ODOO_DB_PASSWORD="${ODOO_DB_PASSWORD:-$(container_env PASSWORD)}"

  if [ -z "${ODOO_DB_HOST}" ] || [ -z "${ODOO_DB_USER}" ] || [ -z "${ODOO_DB_PASSWORD}" ]; then
    echo "Could not read Odoo database connection settings from container ${ODOO_CONTAINER}." >&2
    echo "Set ODOO_DB_HOST, ODOO_DB_USER, and ODOO_DB_PASSWORD, then rerun." >&2
    exit 1
  fi
}

addon_exists() {
  local addon="$1"
  docker exec -i "${ODOO_CONTAINER}" sh -s -- "${addon}" "${ADDONS_PATHS}" <<'SH'
module="$1"
paths="$2"
for path in $paths; do
  if [ -f "$path/$module/__manifest__.py" ] || [ -f "$path/$module/__openerp__.py" ]; then
    exit 0
  fi
done
exit 1
SH
}

check_addons() {
  local missing=()
  for addon in "${REQUIRED_ADDONS[@]}"; do
    if ! addon_exists "${addon}"; then
      missing+=("${addon}")
    fi
  done

  if [ "${#missing[@]}" -gt 0 ]; then
    echo "Missing addons for sector '${SECTOR}':" >&2
    for addon in "${missing[@]}"; do
      echo "  - ${addon}" >&2
    done
    echo "" >&2
    echo "Copy the missing addons into ${ODOO_CONTAINER}:/mnt/extra-addons or add their path with ADDONS_PATHS, then rerun this script." >&2
    exit 1
  fi
}

db_exists() {
  local db="$1"
  local result
  result="$(docker exec -i "${POSTGRES_CONTAINER}" psql -U "${POSTGRES_USER}" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${db}'" | tr -d '[:space:]')"
  [ "${result}" = "1" ]
}

terminate_db() {
  local db="$1"
  docker exec -i "${POSTGRES_CONTAINER}" psql -U "${POSTGRES_USER}" -d postgres -v ON_ERROR_STOP=1 -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${db}' AND pid <> pg_backend_pid();"
}

drop_db() {
  local db="$1"
  terminate_db "${db}"
  docker exec -i "${POSTGRES_CONTAINER}" dropdb -U "${POSTGRES_USER}" --if-exists "${db}"
}

create_db() {
  local db="$1"
  docker exec -i "${POSTGRES_CONTAINER}" createdb -U "${POSTGRES_USER}" "${db}"
}

odoo_config_args=()
if docker exec -i "${ODOO_CONTAINER}" test -f "${ODOO_CONFIG}"; then
  odoo_config_args=(-c "${ODOO_CONFIG}")
fi
odoo_db_args=()

run_odoo_modules() {
  local db="$1"
  local mode="$2"
  local modules="$3"

  echo "Running Odoo module ${mode} on ${db}: ${modules}"
  docker exec -i "${ODOO_CONTAINER}" "${ODOO_BIN}" "${odoo_config_args[@]}" "${odoo_db_args[@]}" -d "${db}" "-${mode}" "${modules}" --stop-after-init --without-demo=all
}

clone_demo() {
  echo "Refreshing ${DEMO_DB} from ${TEMPLATE_DB}"
  terminate_db "${TEMPLATE_DB}"
  drop_db "${DEMO_DB}"
  docker exec -i "${POSTGRES_CONTAINER}" createdb -U "${POSTGRES_USER}" -T "${TEMPLATE_DB}" "${DEMO_DB}"
}

require_containers
load_odoo_db_args
odoo_db_args=(--db_host "${ODOO_DB_HOST}" --db_port "${ODOO_DB_PORT}" --db_user "${ODOO_DB_USER}" --db_password "${ODOO_DB_PASSWORD}")

if [ "${DEPLOY_ADDONS}" = "1" ]; then
  echo "Deploying repository addons to ${ODOO_CONTAINER}"
  bash deployment/deploy_addons_to_docker.sh
  sleep 5
fi

check_addons

if db_exists "${TEMPLATE_DB}"; then
  if [ "${RESET_TEMPLATE}" = "1" ]; then
    echo "Resetting template database ${TEMPLATE_DB}"
    drop_db "${TEMPLATE_DB}"
    create_db "${TEMPLATE_DB}"
    run_odoo_modules "${TEMPLATE_DB}" i "${INSTALL_MODULES}"
  else
    echo "Template database exists; upgrading modules in ${TEMPLATE_DB}"
    terminate_db "${TEMPLATE_DB}"
    run_odoo_modules "${TEMPLATE_DB}" u "${INSTALL_MODULES}"
  fi
else
  echo "Creating template database ${TEMPLATE_DB}"
  create_db "${TEMPLATE_DB}"
  run_odoo_modules "${TEMPLATE_DB}" i "${INSTALL_MODULES}"
fi

if [ "${CLONE_DEMO}" = "1" ]; then
  clone_demo
fi

echo ""
echo "Done."
echo "Template database: ${TEMPLATE_DB}"
echo "Demo database: ${DEMO_DB}"
echo "Demo URL: ${PUBLIC_BASE_URL}/web/login?db=${DEMO_DB}"
