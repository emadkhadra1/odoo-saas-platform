#!/usr/bin/env bash
set -euo pipefail

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-odoo19-db}"
POSTGRES_USER="${POSTGRES_USER:-odoo}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://127.0.0.1:8069}"

db_exists() {
  local db="$1"
  local result
  result="$(docker exec -i "${POSTGRES_CONTAINER}" psql -U "${POSTGRES_USER}" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${db}'" | tr -d '[:space:]')"
  [ "${result}" = "1" ]
}

module_state() {
  local db="$1"
  local module="$2"
  docker exec -i "${POSTGRES_CONTAINER}" psql -U "${POSTGRES_USER}" -d "${db}" -tAc \
    "SELECT COALESCE((SELECT state FROM ir_module_module WHERE name='${module}' LIMIT 1), 'missing');" 2>/dev/null | tr -d '[:space:]' || true
}

print_db_row() {
  local sector="$1"
  local db="$2"
  local module="$3"
  local url="$4"
  local exists="no"
  local state="-"

  if db_exists "${db}"; then
    exists="yes"
    if [ -n "${module}" ]; then
      state="$(module_state "${db}" "${module}")"
      [ -n "${state}" ] || state="unknown"
    fi
  fi

  printf "%-14s %-34s %-7s %-16s %s\n" "${sector}" "${db}" "${exists}" "${state}" "${url}"
}

if ! docker ps --format '{{.Names}}' | grep -Fxq "${POSTGRES_CONTAINER}"; then
  echo "PostgreSQL container is not running: ${POSTGRES_CONTAINER}" >&2
  exit 1
fi

printf "%-14s %-34s %-7s %-16s %s\n" "Sector" "Database" "Exists" "Main module" "URL"
printf "%-14s %-34s %-7s %-16s %s\n" "------" "--------" "------" "-----------" "---"
print_db_row "master" "sass" "odoo_saas_manager" "${PUBLIC_BASE_URL}/web?db=sass"
print_db_row "construction" "tenant_template_construction" "construction_project" "-"
print_db_row "construction" "demo_construction" "construction_project" "${PUBLIC_BASE_URL}/web/login?db=demo_construction"
print_db_row "real-estate" "tenant_template_realestate" "qimam_realestate_demo" "-"
print_db_row "real-estate" "demo_realestate" "qimam_realestate_demo" "${PUBLIC_BASE_URL}/web/login?db=demo_realestate"
print_db_row "hr" "tenant_template_saudi_hr" "qimam_hr_demo" "-"
print_db_row "hr" "demo_hr" "qimam_hr_demo" "${PUBLIC_BASE_URL}/web/login?db=demo_hr"
print_db_row "3pl" "tenant_template_3pl" "delivery_3pl" "-"
print_db_row "3pl" "demo_3pl" "delivery_3pl" "${PUBLIC_BASE_URL}/web/login?db=demo_3pl"
