# C21 Property Listing - Railway Template Installation

## For Odoo Railway Template Users

---

## Step 1: Backup Database

```bash
# Install Railway CLI if not installed
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Get database connection info
railway variables

# Backup using pg_dump
pg_dump "YOUR_DATABASE_URL" > backup_$(date +%Y%m%d).sql
```

Or backup via Odoo UI:
- Settings → Database Manager → Backup

---

## Step 2: Create Volume for Custom Addons

1. Go to **Railway Dashboard** → Your Odoo Service
2. Click **Volumes** tab (or Add → Volume)
3. Create volume:
   - **Mount Path:** `/mnt/extra-addons`
   - **Name:** `custom-addons`
4. Click **Create Volume**

---

## Step 3: Add Environment Variable

In Railway Dashboard → Your Odoo Service → Variables:

Add or update:
```
ODOO_EXTRA_ADDONS=/mnt/extra-addons
```

Or if there's an existing addons path variable, append to it:
```
ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

---

## Step 4: Upload Module to Volume

### Option A: Using Railway Shell

```bash
# Open Railway shell
railway shell

# Inside the container, check volume is mounted
ls -la /mnt/extra-addons

# Exit shell
exit
```

Then use `railway cp` (if available) or create a deployment script.

### Option B: Using GitHub Actions (Recommended)

Create a GitHub repo with your module and set up auto-deploy:

1. Create repo: `c21-odoo-addons`
2. Push your module:
```bash
cd "/Users/kincheonglau/Claude Cowork/odoo19"
git init
git remote add origin https://github.com/YOUR_USERNAME/c21-odoo-addons.git
git add c21_property_listing/
git commit -m "Add c21_property_listing module"
git push -u origin main
```

3. In Railway, connect this repo to your service

### Option C: Manual Upload via Script

Create a one-time deploy script that runs on container start:

```bash
# In Railway Variables, add:
CUSTOM_ADDONS_REPO=https://github.com/YOUR_USERNAME/c21-odoo-addons.git
```

Then add a startup script that clones the repo to `/mnt/extra-addons`

---

## Step 5: Restart Odoo Service

In Railway Dashboard:
1. Click on your Odoo service
2. Click **Restart** (or Deployments → Redeploy)

---

## Step 6: Install Module in Odoo

1. **Login to Odoo** as administrator

2. **Activate Developer Mode:**
   - Settings → Activate Developer Mode (bottom of page)

3. **Update Apps List:**
   - Apps → Click menu (⋮) → Update Apps List
   - Click **Update** in popup

4. **Find and Install:**
   - Apps → Search: `c21` or `property`
   - Find "C21 Property Listing"
   - Click **Install**

---

## Step 7: Verify Installation

### Check in Odoo UI

1. Main menu should show **"C21 Properties"**
2. Click it → Should see:
   - Properties submenu
   - Operators submenu
   - Configuration submenu

### Check Database Tables

Connect to Railway PostgreSQL:

```bash
# Get connection string
railway variables | grep DATABASE

# Connect
psql "YOUR_DATABASE_URL"
```

Run verification:

```sql
-- Check tables created
SELECT table_name
FROM information_schema.tables
WHERE table_name LIKE 'c21_%'
ORDER BY table_name;

-- Expected output:
-- c21_property_amenity
-- c21_property_contact
-- c21_property_image
-- c21_property_listing
-- c21_property_listing_amenity_rel

-- Check amenities loaded (should be 22)
SELECT COUNT(*) as amenity_count FROM c21_property_amenity;

-- List all amenities
SELECT code, name, category FROM c21_property_amenity ORDER BY category, name;

-- Check partner extension
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'res_partner'
  AND column_name IN ('is_property_operator', 'operator_logo_url');
```

---

## Troubleshooting

### Module Not Appearing in Apps

**Check 1:** Volume mounted correctly
```bash
railway shell
ls -la /mnt/extra-addons/c21_property_listing/
# Should show __manifest__.py, models/, views/, etc.
```

**Check 2:** Addons path includes volume
```bash
railway shell
grep -i addons /etc/odoo/odoo.conf
# Or check ODOO_ADDONS_PATH env var
```

**Check 3:** File permissions
```bash
railway shell
ls -la /mnt/extra-addons/
# Files should be readable by odoo user
```

### Installation Fails

Check Odoo logs:
```bash
railway logs --tail 200
```

Common errors:
- `ModuleNotFoundError` → Check __init__.py files
- `ParseError` → XML syntax error in views
- `Access denied` → Login as admin user

### Database Connection

```bash
# Test connection
railway run psql $DATABASE_URL -c "SELECT version();"
```

---

## Quick Test After Installation

1. **Create an Operator:**
   - C21 Properties → Operators → Create
   - Name: "Test Operator"
   - Check "Is Property Operator"
   - Save

2. **Create a Co-working Space:**
   - C21 Properties → Properties → All Properties → Create
   - Listing Type: Co-working Space
   - Name: "Test Space"
   - District: Central
   - Operator: Test Operator
   - Capacity: 100
   - Save

3. **Test Workflow:**
   - Click "Submit for Review"
   - Click "Approve"
   - Click "Publish"

4. **Check Amenities:**
   - Configuration → Amenities
   - Should see 22 pre-loaded amenities

---

## File Structure on Railway

After installation, your Railway container should have:

```
/mnt/extra-addons/
└── c21_property_listing/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── property_listing.py
    │   ├── property_image.py
    │   ├── property_amenity.py
    │   ├── property_contact.py
    │   └── res_partner.py
    ├── views/
    │   ├── property_listing_views.xml
    │   ├── property_operator_views.xml
    │   ├── property_amenity_views.xml
    │   └── menu.xml
    ├── security/
    │   ├── security.xml
    │   └── ir.model.access.csv
    └── data/
        └── property_amenity_data.xml
```

---

## Need Help?

If you encounter issues:

1. Share Railway logs: `railway logs --tail 100`
2. Share Odoo error message from browser
3. Check PostgreSQL tables exist

---

*For Odoo 19 on Railway Template*
