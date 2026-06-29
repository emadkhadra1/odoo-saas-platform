#!/usr/bin/env bash
set -euo pipefail

ODOO_CONTAINER="${ODOO_CONTAINER:-odoo19}"
EXTRA_ADDONS_PATH="${EXTRA_ADDONS_PATH:-/mnt/extra-addons}"

copy_addon() {
  local source_path="$1"
  local addon_name
  addon_name="$(basename "$source_path")"

  echo "Deploying ${addon_name}"
  docker exec -u 0 -i "${ODOO_CONTAINER}" rm -rf "${EXTRA_ADDONS_PATH:?}/${addon_name}"
  docker cp "${source_path}" "${ODOO_CONTAINER}:${EXTRA_ADDONS_PATH}/"
  docker exec -u 0 -i "${ODOO_CONTAINER}" chown -R odoo:root "${EXTRA_ADDONS_PATH}/${addon_name}"
}

copy_addon odoo_saas_manager
copy_addon odoo_saas_website

for addon in sector_addons/odoo19/*; do
  if [ -d "$addon" ] && [ -f "$addon/__manifest__.py" ]; then
    copy_addon "$addon"
  fi
done

docker exec -u 0 -i "${ODOO_CONTAINER}" python3 - <<'PY'
from pathlib import Path

config_path = Path("/etc/odoo/odoo.conf")
module_name = "odoo_saas_website"
lines = config_path.read_text().splitlines()
for index, line in enumerate(lines):
    if line.strip().startswith("server_wide_modules"):
        key, _, value = line.partition("=")
        modules = [item.strip() for item in value.split(",") if item.strip()]
        if module_name not in modules:
            modules.append(module_name)
            lines[index] = f"{key.strip()} = {','.join(modules)}"
        break
else:
    lines.append(f"server_wide_modules = base,web,{module_name}")
config_path.write_text("\n".join(lines) + "\n")
PY

docker restart "${ODOO_CONTAINER}"

echo "Addons deployed. Open Odoo Apps, update the apps list, then upgrade/install the needed modules."
