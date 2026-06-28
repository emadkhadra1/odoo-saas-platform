#!/usr/bin/env bash
set -euo pipefail

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-odoo19-db}"
POSTGRES_USER="${POSTGRES_USER:-odoo}"

clone_db() {
  local template_db="$1"
  local demo_db="$2"

  echo "Refreshing ${demo_db} from ${template_db}"
  docker exec -i "${POSTGRES_CONTAINER}" psql -U "${POSTGRES_USER}" -d postgres -v ON_ERROR_STOP=1 -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('${template_db}', '${demo_db}') AND pid <> pg_backend_pid();"
  docker exec -i "${POSTGRES_CONTAINER}" dropdb -U "${POSTGRES_USER}" --if-exists "${demo_db}"
  docker exec -i "${POSTGRES_CONTAINER}" createdb -U "${POSTGRES_USER}" -T "${template_db}" "${demo_db}"
}

clone_db tenant_template_construction demo_construction
clone_db tenant_template_realestate demo_realestate
clone_db tenant_template_saudi_hr demo_hr
clone_db tenant_template_3pl demo_3pl

echo "Demo databases are ready."
