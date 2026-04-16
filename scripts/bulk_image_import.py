#!/usr/bin/env python3
"""
Bulk import: download images from URL into binary field for all
c21.property.image records that have image_url but no image.
Run inside container: python3 /usr/local/bin/bulk_image_import.py
"""
import sys
import os

# Inject Odoo config via env vars present in the running container
os.environ.setdefault('PGHOST', os.environ.get('ODOO_DATABASE_HOST', 'postgres.railway.internal'))
os.environ.setdefault('PGPORT', os.environ.get('ODOO_DATABASE_PORT', '5432'))
os.environ.setdefault('PGUSER', os.environ.get('ODOO_DATABASE_USER', 'railway'))
os.environ.setdefault('PGPASSWORD', os.environ.get('ODOO_DATABASE_PASSWORD', ''))

import odoo
import odoo.tools.config as config

db_name = os.environ.get('ODOO_DATABASE_NAME', 'railway')
db_host = os.environ.get('ODOO_DATABASE_HOST', 'postgres.railway.internal')
db_port = os.environ.get('ODOO_DATABASE_PORT', '5432')
db_user = os.environ.get('ODOO_DATABASE_USER', 'railway')
db_pass = os.environ.get('ODOO_DATABASE_PASSWORD', '')

config.parse_config([
    '-c', '/etc/odoo/odoo.conf',
    f'--db_host={db_host}',
    f'--db_port={db_port}',
    f'--db_user={db_user}',
    f'--db_password={db_pass}',
])

from odoo import api, SUPERUSER_ID
from odoo.orm.registry import Registry

print(f'[bulk_image_import] Connecting to db={db_name} host={db_host}')
registry = Registry.new(db_name)
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Model = env['c21.property.image']
    missing = Model.search([('image_url', '!=', False), ('image', '=', False)])
    print(f'[bulk_image_import] Found {len(missing)} records with URL but no image')
    ok = 0
    fail_list = []
    for rec in missing:
        try:
            data = rec._download_image_from_url(rec.image_url)
            if data:
                rec.write({'image': data})
                ok += 1
                print(f'  OK  id={rec.id} url={rec.image_url[:60]}')
            else:
                fail_list.append((rec.id, rec.image_url, 'no_data'))
        except Exception as e:
            fail_list.append((rec.id, rec.image_url, str(e)))
    cr.commit()
    remaining = Model.search_count([('image_url', '!=', False), ('image', '=', False)])
    print(f'[bulk_image_import] Done: success={ok}, failed={len(fail_list)}')
    if fail_list:
        for fid, furl, reason in fail_list:
            print(f'  FAIL id={fid} reason={reason} url={furl[:80]}')
    print(f'[bulk_image_import] Remaining without image: {remaining}')
