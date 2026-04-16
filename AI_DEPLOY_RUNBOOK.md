# Odoo 19 + Railway Deployment Runbook (C21 Modules)

## Problem Summary

Deploying with `railway up` updated the Docker image, but Odoo still loaded old module code.

Root cause:

- Odoo loads custom modules from `/var/lib/odoo/addons/19.0` first.
- That path is on a persistent Railway volume.
- Volume files are not replaced by image deploys.
- New code existed in `/mnt/extra-addons`, but runtime loaded old files from volume.

## What Was Changed

### 1) Startup sync script added

File changed:

- `scripts/sync_addons_and_start.sh`

Script behavior:

- Copies these modules from image path to volume path:
  - `c21_property_listing`
  - `c21_admin_dashboard`
- Source: `/mnt/extra-addons`
- Destination: `/var/lib/odoo/addons/19.0`
- Then starts Odoo.

### 2) Dockerfile updated

File changed:

- `Dockerfile`

Updates:

- Copies `scripts/sync_addons_and_start.sh` into image.
- Marks script executable.
- Sets `ENTRYPOINT` to the sync script.

### 3) Odoo safe-eval fix in server action code

File changed:

- `c21_property_listing/data/server_actions.xml`

Fix applied:

- Replaced forbidden attribute assignment:
  - `img.image = image_data`
- With safe ORM write:
  - `img.write({'image': image_data})`

This removed `STORE_ATTR` parse errors during module upgrade.

## Current Runtime Reality

Even after image changes, current Railway runtime still starts directly with:

- `/usr/bin/python3 /usr/bin/odoo --http-port=8080`

So in practice, manual sync is still required before upgrade.

## Proven Deployment Procedure

Use this exact sequence after code changes:

```bash
cd "/Users/kincheonglau/Claude Cowork/odoo19"
railway up
railway ssh -- /usr/local/bin/sync_addons_and_start.sh
```

Then in Odoo UI:

1. Apps -> Update Apps List
2. Upgrade `C21 Property Management`
3. Hard refresh browser

## Quick Verification Commands

Check runtime addons path order:

```bash
railway logs --tail 200 | grep -i "addons paths"
```

Check files in volume module path:

```bash
railway ssh ls -la /var/lib/odoo/addons/19.0/c21_property_listing/views/
```

Check files in image module path:

```bash
railway ssh ls -la /mnt/extra-addons/c21_property_listing/views/
```

## If Upgrade Fails Again

Pull the error quickly:

```bash
railway logs --tail 250 | grep -A 30 -E "ERROR|Traceback|ParseError|c21_property_listing"
```

Typical pattern seen:

- `forbidden opcode(s) ... STORE_ATTR`
- Cause: server action Python code using attribute assignment in XML code blocks.

Fix pattern:

- Use `record.write({...})` instead of `record.field = value`.

## Is This a Common Problem?

Yes. This is common when:

- Odoo custom addons are loaded from a persistent volume, and
- deploys only update image content.

If source-of-truth is volume, you must sync volume on each deploy.

## Recommended Next Improvement

Make startup sync truly automatic by ensuring Railway service start command does not bypass image `ENTRYPOINT`.

Target behavior:

- Deploy image
- Container starts
- Sync script runs automatically
- Odoo starts
- Only then upgrade module in UI
