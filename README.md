# C21 Odoo 19 Custom Addons

Custom Odoo 19 modules for C21 property management, deployed on Railway.

## Quick Start for New Developers

1. Clone the repository
2. Read the documentation in order (see below)
3. Set up local Odoo 19 environment
4. Deploy to Railway when ready

## Documentation Index

Read these documents in order for full context:

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `README.md` | Project overview (this file) | First |
| `WORK_SUMMARY.md` | Completed work & reporting format | Before starting work |
| `LAYOUT_GUIDELINES.md` | UI/UX standards for forms & views | Before writing views |
| `AI_DEPLOY_RUNBOOK.md` | Deployment procedures | Before deploying |
| `CHANGELOG_v2.md` | Version history & breaking changes | When upgrading |
| `IMAGE_MIGRATION_GUIDE.md` | Image storage migration | If working on images |
| `EXPORT_IMPORT_GUIDE.md` | Data import/export procedures | If migrating data |

## Prerequisites

- Python 3.10+
- Odoo 19.0
- PostgreSQL 14+
- Railway CLI (for deployment)

## Modules

| Module | Description | Version | Status |
|--------|-------------|---------|--------|
| `c21_property_listing` | Property listing for co-working & leasing | 19.0.2.0.0 | Active |

## Module: c21_property_listing

### Features

- Unified property management (co-working + leasing)
- Bilingual support (English/Chinese)
- 21 Hong Kong districts
- 22 pre-loaded amenities
- Approval workflow
- Operator management via res.partner
- Image storage with auto-download from URLs

### Database Tables

| Table | Purpose |
|-------|---------|
| `c21_property_listing` | Main properties |
| `c21_property_image` | Property images (stored in DB) |
| `c21_property_amenity` | Amenities master data |
| `c21_property_contact` | Property contacts |
| `c21_property_listing_amenity_rel` | Property-Amenity M2M |
| `res_partner` | Extended with operator fields |

## Local Development

### Option 1: Docker (Recommended)

```bash
# Pull Odoo 19 image
docker pull odoo:19.0

# Run with local addons mounted
docker run -d \
  -v $(pwd)/c21_property_listing:/mnt/extra-addons/c21_property_listing \
  -p 8069:8069 \
  --name odoo19-dev \
  odoo:19.0
```

### Option 2: Native Installation

```bash
# Clone Odoo 19
git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git

# Install dependencies
pip install -r odoo/requirements.txt

# Run with custom addons
./odoo/odoo-bin -d c21_dev --addons-path=odoo/addons,./c21_property_listing
```

### After Setup

1. Access Odoo at `http://localhost:8069`
2. Create database or use existing
3. Apps -> Update Apps List
4. Search "C21 Property" -> Install

## Deployment (Railway)

**Important:** We use manual Railway CLI deployment, not GitHub Actions.

### Quick Deploy

```bash
# Commit your changes
git add .
git commit -m "Your changes"
git push origin main

# Deploy to Railway
railway up --detach

# After deploy completes, upgrade in Odoo UI:
# Apps -> C21 Property Management -> Upgrade
```

### Full Deploy Procedure

See `AI_DEPLOY_RUNBOOK.md` for detailed instructions including:
- Sync script execution
- Volume management
- Troubleshooting

### Railway Architecture

```
Image Build:
  /mnt/extra-addons/c21_property_listing  (from git)
       |
       | sync_addons_and_start.sh
       v
Runtime Volume:
  /var/lib/odoo/addons/19.0/c21_property_listing  (persistent)
```

## Contributing

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring

### Commit Messages

Use clear, descriptive messages:
```
Add image download button to property form
Fix kanban view error in Odoo 17+
Update operator form to hide chatter
```

### Before Committing

1. Test changes locally
2. Follow `LAYOUT_GUIDELINES.md` for UI changes
3. Update `CHANGELOG_v2.md` for significant changes

### Code Style

- Follow Odoo 19 conventions
- Use bilingual labels: `"English / 中文"`
- Hide technical fields from users
- Use `invisible` attribute for conditional display

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| View error after XML changes | Delete cached view in Settings -> Technical -> Views |
| `kanban_image` not a function | Replace with `<field widget="image"/>` (Odoo 17+ breaking change) |
| Changes not appearing | Redeploy + Upgrade module + Hard refresh browser |
| Module not found | Run sync script, then Update Apps List |

### Odoo 17+ Breaking Changes

See `WORK_SUMMARY.md` for details on compatibility fixes applied.

## Version

- **Odoo**: 19.0
- **Module Version**: 19.0.2.0.0
- **Last Updated**: April 2026

## Support

For questions or issues:
1. Check existing documentation
2. Review `WORK_SUMMARY.md` for past solutions
3. Contact project maintainers
