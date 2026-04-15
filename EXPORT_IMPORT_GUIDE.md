# C21 Custom Modules - Export/Import Guide

## Custom Modules

| Module Folder | Display Name | Description |
|---------------|--------------|-------------|
| `c21_property_listing` | C21 Property Management | Co-working and leasing property management |
| `c21_admin_dashboard` | C21 Admin Dashboard | Admin dashboard with changelog tracking |

## Export Modules

### Method 1: Git Clone (Recommended)
```bash
git clone https://github.com/lojul/c21-odoo-addons.git
```

### Method 2: Download ZIP
1. Go to https://github.com/lojul/c21-odoo-addons
2. Click "Code" → "Download ZIP"
3. Extract the modules you need

### Method 3: Copy Folders
Copy these folders from the source system:
- `c21_property_listing/`
- `c21_admin_dashboard/`

## Import to New Odoo System

### Step 1: Copy Modules to Addons Path

Common addons paths:
- Docker: `/mnt/extra-addons/` or `/var/lib/odoo/addons/19.0/`
- Linux: `/opt/odoo/addons/` or `~/.local/share/Odoo/addons/19.0/`
- Railway: `/var/lib/odoo/addons/19.0/`

```bash
# Example for Railway/Docker
cp -r c21_property_listing /var/lib/odoo/addons/19.0/
cp -r c21_admin_dashboard /var/lib/odoo/addons/19.0/
```

### Step 2: Update Apps List
1. Login to Odoo as admin
2. Enable Developer Mode: Settings → Activate Developer Mode
3. Apps → Click ⋮ (menu) → Update Apps List → Update

### Step 3: Install Modules
1. Apps → Search "C21"
2. Install "C21 Property Management"
3. Install "C21 Admin Dashboard" (optional)

## Module Dependencies

```
c21_property_listing
├── depends: base, mail
└── (standalone - no custom dependencies)

c21_admin_dashboard
├── depends: base
└── (standalone - no custom dependencies)
```

## Data Migration

### Export Data from Source System

```sql
-- Export properties
COPY (SELECT * FROM c21_property_listing) TO '/tmp/properties.csv' WITH CSV HEADER;

-- Export amenities
COPY (SELECT * FROM c21_property_amenity) TO '/tmp/amenities.csv' WITH CSV HEADER;

-- Export operators
COPY (SELECT * FROM res_partner WHERE is_property_operator = true) TO '/tmp/operators.csv' WITH CSV HEADER;
```

### Import Data to Target System

Use Odoo's import feature:
1. Go to the list view (Properties, Operators, etc.)
2. Click ⚙ → Import records
3. Upload CSV file
4. Map columns and import

## Verify Installation

After installation, verify:
1. C21 Properties app appears in main menu
2. Properties menu works
3. Operators menu works
4. Configuration → Amenities shows 22 pre-loaded items

## Troubleshooting

### Module Not Appearing
1. Check addons_path includes your module location
2. Restart Odoo service
3. Update Apps List again

### Installation Error
1. Check Odoo logs: `tail -f /var/log/odoo/odoo.log`
2. Verify Python dependencies: `base`, `mail` modules installed
3. Check file permissions

### Data Import Issues
1. Export with Odoo's native export (preserves relations)
2. Import in correct order: Amenities → Operators → Properties

## Version Compatibility

- Odoo Version: 19.0
- Python: 3.10+
- PostgreSQL: 12+
