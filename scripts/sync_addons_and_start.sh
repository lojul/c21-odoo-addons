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

echo "[startup-sync] Starting Odoo directly (bypassing slow init)"

# Build addons path
ADDONS_PATH="/var/lib/odoo/addons/19.0,/usr/lib/python3/dist-packages/odoo/addons"

# Start Odoo directly - NO --init flag!
exec /usr/bin/python3 /usr/bin/odoo \
  --http-port=8080 \
  --proxy-mode \
  --db_host="${ODOO_DATABASE_HOST:-localhost}" \
  --db_port="${ODOO_DATABASE_PORT:-5432}" \
  --db_user="${ODOO_DATABASE_USER:-odoo}" \
  --db_password="${ODOO_DATABASE_PASSWORD:-odoo}" \
  --database="${ODOO_DATABASE_NAME:-odoo}" \
  --db_maxconn="${DB_MAXCONN:-64}" \
  --addons-path="${ADDONS_PATH}" \
  --data-dir=/var/lib/odoo \
  --limit-time-cpu="${LIMIT_TIME_CPU:-600}" \
  --limit-time-real="${LIMIT_TIME_REAL:-1200}" \
  --workers="${WORKERS:-0}" \
  --without-demo=True \
  "$@"
