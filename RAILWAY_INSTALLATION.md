# C21 Property Listing - Railway Installation Guide

## Overview

This guide explains how to deploy the `c21_property_listing` module to your Odoo 19 instance on Railway.

---

## Method 1: Git-based Deployment (Recommended)

### Step 1: Push Module to Git Repository

If your Odoo deployment pulls from git:

```bash
# Navigate to your Odoo 19 addons directory
cd "/Users/kincheonglau/Claude Cowork/odoo19"

# Initialize git if not already done
git init

# Add and commit the module
git add c21_property_listing/
git commit -m "Add c21_property_listing module"

# Push to your repository
git push origin main
```

### Step 2: Configure Addons Path on Railway

In Railway, set the environment variable:

```
ODOO_ADDONS_PATH=/app/odoo/addons,/app/custom-addons
```

Or if using `odoo.conf`:

```ini
[options]
addons_path = /app/odoo/addons,/app/custom-addons
```

### Step 3: Deploy

Railway will auto-deploy on git push, or manually trigger:

```bash
railway up
```

---

## Method 2: Volume Mount (Persistent Storage)

### Step 1: Create Volume in Railway

1. Go to Railway Dashboard
2. Select your Odoo service
3. Add a Volume: `/app/custom-addons`

### Step 2: Copy Module Files

Use Railway CLI to copy files:

```bash
# Connect to Railway shell
railway run bash

# Inside container, create directory
mkdir -p /app/custom-addons/c21_property_listing

# Exit and copy files (from local)
railway cp ./c21_property_listing /app/custom-addons/
```

Or use `rsync`/`scp` if SSH is available.

### Step 3: Update odoo.conf

```ini
[options]
addons_path = /app/odoo/addons,/app/custom-addons
```

### Step 4: Restart Service

```bash
railway service restart
```

---

## Method 3: Docker Build (If Using Custom Dockerfile)

### Step 1: Update Dockerfile

```dockerfile
FROM odoo:19.0

# Copy custom addons
COPY ./odoo19/c21_property_listing /mnt/extra-addons/c21_property_listing

# Update addons path
ENV ODOO_ADDONS_PATH=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
```

### Step 2: Build and Deploy

```bash
railway up --build
```

---

## Post-Deployment: Install Module

### Option A: Via Odoo Web UI

1. Login to Odoo as admin
2. Go to **Apps**
3. Click **Update Apps List** (under dropdown menu)
4. Search for **"C21 Property"**
5. Click **Install**

### Option B: Via Command Line

```bash
# Connect to Railway shell
railway run bash

# Run Odoo install command
odoo -d your_database -i c21_property_listing --stop-after-init
```

### Option C: Via Database Manager

If you have access to database manager:
1. Settings → Technical → Modules → Update Modules List
2. Search "c21_property_listing"
3. Click Install

---

## Verify Installation

### 1. Check Module is Installed

In Odoo:
- Apps → Search "C21" → Should show "Installed"

### 2. Check Menu Exists

- Main menu should show "C21 Properties"

### 3. Check Database Tables

Connect to your PostgreSQL database on Railway:

```bash
# Get database URL from Railway
railway variables

# Connect to PostgreSQL
psql $DATABASE_URL
```

Then run:

```sql
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_name LIKE 'c21_%';

-- Should return:
-- c21_property_listing
-- c21_property_image
-- c21_property_amenity
-- c21_property_contact
-- c21_property_listing_amenity_rel

-- Check amenities loaded
SELECT COUNT(*) FROM c21_property_amenity;
-- Should return: 22

-- Check res_partner extended
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'res_partner'
  AND column_name LIKE '%operator%';
-- Should return:
-- is_property_operator
-- operator_logo_url
```

---

## Troubleshooting

### Module Not Showing in Apps

1. Check addons_path is correct
2. Run "Update Apps List"
3. Clear browser cache
4. Check Odoo logs for errors

```bash
railway logs
```

### Installation Fails

Check logs for specific error:

```bash
railway logs --tail 100
```

Common issues:
- Missing dependencies: Install `mail` module first
- Syntax error: Check Python/XML files
- Permission issue: Check file ownership

### Database Connection Error

```bash
# Verify database connection
railway run bash
psql $DATABASE_URL -c "SELECT 1"
```

---

## Rollback

If something goes wrong:

### Option 1: Uninstall Module

```bash
railway run bash
odoo -d your_database -u c21_property_listing --stop-after-init
```

Then in Odoo: Apps → C21 Property Listing → Uninstall

### Option 2: Restore Database Backup

```bash
# If you made a backup before installation
pg_restore -d $DATABASE_URL backup_file.dump
```

### Option 3: Remove Tables Manually

```sql
-- Connect to PostgreSQL
DROP TABLE IF EXISTS c21_property_listing_amenity_rel CASCADE;
DROP TABLE IF EXISTS c21_property_image CASCADE;
DROP TABLE IF EXISTS c21_property_contact CASCADE;
DROP TABLE IF EXISTS c21_property_listing CASCADE;
DROP TABLE IF EXISTS c21_property_amenity CASCADE;

-- Clean Odoo system tables
DELETE FROM ir_module_module WHERE name = 'c21_property_listing';
DELETE FROM ir_model_data WHERE module = 'c21_property_listing';
```

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ODOO_ADDONS_PATH` | Custom addons location | `/app/custom-addons` |
| `DATABASE_URL` | PostgreSQL connection | Auto-set by Railway |
| `ODOO_ADMIN_PASSWORD` | Admin password | Your password |

---

## Next Steps After Installation

1. **Create an Operator** - Go to Operators menu, add a co-working operator
2. **Create a Property** - Go to Properties → All Properties → Create
3. **Test Workflow** - Submit for review, approve, publish
4. **Verify Amenities** - Check Configuration → Amenities (22 pre-loaded)

---

*Document Version: 1.0*
*For: Odoo 19 on Railway*
