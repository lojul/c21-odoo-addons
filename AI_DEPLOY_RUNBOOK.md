# Odoo 19 + Railway Deployment Runbook (C21 Modules)

## Current Standard

Use manual Railway CLI deployment from the local workspace. Do not rely on GitHub Actions for deployment.

Reason:

- Railway CLI deploy from the local machine works reliably.
- GitHub Actions auto-deploy was disabled because Railway auth from GitHub was not reliable in this setup.
- Odoo still loads custom addons from the persistent volume first, so post-deploy sync is required.

## Root Cause

Deploying with `railway up` updates the image, but Odoo loads custom modules from the persistent volume first.

- Odoo loads custom modules from `/var/lib/odoo/addons/19.0`
- That path is on a persistent Railway volume
- New image code is copied to `/mnt/extra-addons`
- If the volume is not synced, Odoo continues using old code from the volume

## Required Runtime Pieces

### 1. Sync script

File:

- `scripts/sync_addons_and_start.sh`

Behavior:

- Copies `c21_property_listing` and `c21_admin_dashboard`
- Source: `/mnt/extra-addons`
- Destination: `/var/lib/odoo/addons/19.0`

### 2. Docker image contents

Files involved:

- `Dockerfile`
- `scripts/sync_addons_and_start.sh`

### 3. Deployment target

Use these explicit Railway identifiers:

- Project: `357d3bd3-d006-46ad-aa91-7ac88b3fb7c1`
- Service: `Odoo`
- Environment: `production`

## Standard Deploy Procedure

Use this exact sequence after code changes:

```bash
cd "/Users/kincheonglau/Claude Cowork/odoo19"
railway up --detach --project 357d3bd3-d006-46ad-aa91-7ac88b3fb7c1 --service Odoo --environment production
railway ssh --project 357d3bd3-d006-46ad-aa91-7ac88b3fb7c1 --service Odoo --environment production -- /usr/local/bin/sync_addons_and_start.sh
```

Then in Odoo UI:

1. Apps -> Upgrade the affected module
2. Hard refresh browser

For this repo, most UI/view changes require upgrading:

- `C21 Property Management`

## Important Note About GitHub Actions

Current status:

- Auto GitHub Action deploy is disabled
- Workflow file remains in the repo for manual use only
- Pushes to `main` should no longer trigger deployment automatically

Do not wait for GitHub Actions before checking production. The real deploy path is manual Railway CLI.

## How To Verify Deployment

Check latest Railway deployment:

```bash
cd "/Users/kincheonglau/Claude Cowork/odoo19"
railway deployment list --service Odoo | sed -n '1,6p'
```

Re-run sync if needed:

```bash
cd "/Users/kincheonglau/Claude Cowork/odoo19"
railway ssh --project 357d3bd3-d006-46ad-aa91-7ac88b3fb7c1 --service Odoo --environment production -- /usr/local/bin/sync_addons_and_start.sh
```

Check volume module path:

```bash
railway ssh --project 357d3bd3-d006-46ad-aa91-7ac88b3fb7c1 --service Odoo --environment production -- ls -la /var/lib/odoo/addons/19.0/c21_property_listing/views/
```

Check image module path:

```bash
railway ssh --project 357d3bd3-d006-46ad-aa91-7ac88b3fb7c1 --service Odoo --environment production -- ls -la /mnt/extra-addons/c21_property_listing/views/
```

## If Something Looks Unchanged

Use this order:

1. Confirm `railway up` finished successfully
2. Run sync script again
3. Upgrade the affected Odoo module
4. Hard refresh browser

If the UI still looks stale, assume volume code is stale before assuming the deploy failed.

## Common Failure Pattern

For module upgrade parse errors in server actions:

- Bad pattern: `record.field = value`
- Good pattern: `record.write({'field': value})`

Known example already fixed in this repo:

- `c21_property_listing/data/server_actions.xml`

## Future AI Guidance

When the user asks to deploy:

1. Make code changes
2. Commit and push if requested
3. Deploy manually with Railway CLI
4. Run the sync script manually
5. Tell the user to upgrade the module in Odoo if the change affects views, assets, or XML

Do not rely on GitHub Actions as the primary deploy mechanism for this project.
