# C21 Odoo 19 Custom Addons

Custom Odoo 19 modules for C21 property management.

## Modules

| Module | Description | Status |
|--------|-------------|--------|
| `c21_property_listing` | Property listing for co-working & leasing | Phase 1 Complete |

## Deployment

This repository is connected to Railway for automatic deployment.

### Railway Setup

1. Runtime persistent addons path: /var/lib/odoo/addons/19.0
2. Image addons source path: /mnt/extra-addons
3. Container startup script auto-syncs modules from image to volume before Odoo starts

### To Deploy

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Railway will deploy a new image, and startup sync will copy the latest modules into the mounted volume automatically.

After deploy:

1. Open Odoo Apps
2. Click Update Apps List
3. Upgrade C21 modules

## Module: c21_property_listing

### Features
- Unified property management (co-working + leasing)
- Bilingual support (English/Chinese)
- 21 Hong Kong districts
- 22 pre-loaded amenities
- Approval workflow
- Operator management via res.partner

### Database Tables
- `c21_property_listing` - Main properties
- `c21_property_image` - Image URLs (CDN)
- `c21_property_amenity` - Amenities master
- `c21_property_contact` - Property contacts
- `c21_property_listing_amenity_rel` - M2M relation
- `res_partner` - Extended with operator fields

## Installation

After deployment to Railway:

1. Login to Odoo as admin
2. Apps → Update Apps List
3. Search "C21 Property"
4. Click Install

## Version

- Odoo: 19.0
- Module Version: 19.0.1.0.0
