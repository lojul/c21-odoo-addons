#!/bin/bash
set -euo pipefail

SRC_ROOT="/mnt/extra-addons"
DST_ROOT="/var/lib/odoo/addons/19.0"
MODULES=("c21_property_listing" "c21_admin_dashboard")

echo "[startup-sync] Syncing custom addons from image to persistent volume"

mkdir -p "${DST_ROOT}"

for module in "${MODULES[@]}"; do
  src="${SRC_ROOT}/${module}"
  dst="${DST_ROOT}/${module}"

  if [[ ! -d "${src}" ]]; then
    echo "[startup-sync] WARNING: source module not found: ${src}"
    continue
  fi

  rm -rf "${dst}"
  cp -a "${src}" "${dst}"
  echo "[startup-sync] Updated ${module} -> ${dst}"
done

echo "[startup-sync] Starting Odoo"
exec /entrypoint.sh "$@"
