# Property Image Migration Guide

## Overview

The C21 Property Management module has been updated to **store actual images** instead of just URLs. This provides better performance, offline access, and automatic image resizing.

## What Changed

### Before (v19.0.1.x.x)
- Images stored as URLs pointing to external CDN
- Fields: `image_url`, `thumbnail_url`
- Required external CDN access to view images

### After (v19.0.2.0.0)
- Images stored directly in Odoo database
- Fields: `image`, `image_medium` (512x512), `image_small` (256x256)
- Legacy URL fields kept for migration
- Automatic download from URLs when pasting
- Automatic resizing for different display sizes

## Upgrade Process

### Step 1: Update Module

```bash
# If using Railway
git pull origin main
railway up

# Or manually copy files and restart Odoo
```

### Step 2: Upgrade Module in Odoo

1. Login to Odoo as admin
2. Go to **Apps** → Search "C21"
3. Click **Upgrade** button
4. Wait for upgrade to complete

### Step 3: Download Existing Images

You have **three options** to migrate existing images from URLs:

#### Option A: Automatic Migration (Recommended)

The module will automatically download images when you create or update records with URLs:

```python
# When creating new images
image_vals = {
    'property_id': property.id,
    'name': 'Living Room',
    'image_url': 'https://example.com/image.jpg'  # Image auto-downloads
}
env['c21.property.image'].create(image_vals)
```

#### Option B: Bulk Download via UI (Easiest)

1. Go to **C21 Properties** → **Properties** → **All Properties**
2. Select properties that need image migration
3. Click **Action** → **Download Images from URLs**
4. Wait for notification showing download results

OR for all images:

1. Go to **C21 Properties** → **Configuration** → **All Images**
2. Select images with URLs but no image data
3. Click **Action** → **🔄 Download All Images from URLs**

#### Option C: Migration Script (Most Control)

Use the Python migration script for full control:

```bash
# Connect to Odoo shell
odoo shell -d your_database -c /etc/odoo.conf

# Run migration
from c21_property_listing.migrations.migrate_images import migrate_all_images
result = migrate_all_images(env)
print(f"Success: {result['success']}, Failed: {result['failed']}")
```

Or migrate specific properties:

```python
from c21_property_listing.migrations.migrate_images import migrate_property_images

# Get property IDs
property_ids = [1, 2, 3, 4]  # Replace with your IDs

# Migrate
result = migrate_property_images(env, property_ids)
print(f"Success: {result['success']}, Failed: {result['failed']}")
```

## New Features

### 1. Auto-Download from URL

When entering a URL in the `image_url` field, the image automatically downloads:

1. Go to any property
2. Click **Images** tab
3. In the image list, paste a URL in the **Image URL** field
4. Save or click the download button
5. Image downloads automatically!

### 2. Multiple Image Sizes

Images are automatically resized to three sizes:
- **Full**: Original (max 1920x1920)
- **Medium**: 512x512 (for lists)
- **Small**: 256x256 (for thumbnails)

### 3. Image Gallery View

View all images across all properties:

**C21 Properties → Configuration → All Images**

Available views:
- **Kanban**: Visual gallery with image previews
- **List**: Detailed list with thumbnails
- **Form**: Full image details and management

### 4. Manual Download Button

Each image has a **Download from URL** button to refresh/re-download from the URL.

## Troubleshooting

### Images Not Downloading

**Problem**: URLs provided but images not downloading

**Solutions**:
1. Check URL is accessible (test in browser)
2. Verify Odoo server has internet access
3. Check firewall/proxy settings
4. Look at Odoo logs for error details:
   ```bash
   railway logs --tail 100
   # Or
   tail -f /var/log/odoo/odoo.log
   ```

### Download Failed Notification

**Problem**: Some images failed to download

**Possible Causes**:
- URL is dead/broken (404 error)
- Server timeout (image too large or slow connection)
- Authentication required
- Invalid image format

**Solution**: Check failed URLs manually and replace with working URLs

### Missing requests Library

**Problem**: Error: "No module named 'requests'"

**Solution**:
```bash
pip3 install requests
# Or in Railway, add to requirements.txt
```

### Database Size Increased

**Expected**: Images are now stored in database, so size will increase

**Recommendation**:
- Monitor database size on Railway
- Consider cleanup of old/unused images
- Use Railway's database backup features

## Legacy URL Fields

The `image_url` and `thumbnail_url` fields are **kept for backward compatibility**:

- Hidden by default in views
- Used for migration
- Can be used to re-download/refresh images
- Will be removed in future major version (v20.0)

## Best Practices

### For New Images

**Option 1: Direct Upload (Recommended)**
1. Use the **Image** field
2. Click to upload from computer
3. Odoo handles resizing automatically

**Option 2: URL Import**
1. Paste URL in **Image URL** field
2. Image downloads automatically
3. URL is saved for reference

### For Bulk Import

```python
# Prepare image data
images_data = [
    {
        'property_id': 1,
        'name': 'Living Room',
        'image_url': 'https://example.com/image1.jpg',
        'is_cover': True,
        'sequence': 1
    },
    {
        'property_id': 1,
        'name': 'Kitchen',
        'image_url': 'https://example.com/image2.jpg',
        'sequence': 2
    }
]

# Create images (auto-downloads from URLs)
env['c21.property.image'].create(images_data)
```

### Image Naming Convention

Use descriptive names for better organization:
- "Exterior - Front View"
- "Lobby - Main Entrance"
- "Office - Workspace Area"
- "Amenities - Gym"

## Performance Considerations

### Database Size
- Full HD image (~2MB) → ~200KB when resized to 1920x1920
- Medium size (~50KB) for lists
- Small size (~20KB) for thumbnails

### Memory Usage
- Odoo caches image data efficiently
- Three sizes reduce bandwidth for different views
- Consider cleanup of old unused images

### Railway Deployment
- Images deploy with the database
- Database backups include images
- Consider Railway's storage limits

## API Changes

If using the REST API (Phase 3):

### Before
```json
{
  "image_url": "https://cdn.example.com/image.jpg",
  "thumbnail_url": "https://cdn.example.com/thumb.jpg"
}
```

### After
```json
{
  "image": "base64_encoded_image_data",
  "image_medium": "base64_encoded_medium_image",
  "image_small": "base64_encoded_small_image",
  "image_url": "https://cdn.example.com/image.jpg"  // Optional, for reference
}
```

## Rollback Plan

If you need to rollback:

1. Keep a database backup before upgrade
2. To restore URLs-only functionality:
   - Restore database backup
   - Downgrade module to v19.0.1.x.x

## Support

For issues or questions:
1. Check Odoo logs for detailed error messages
2. Review this guide
3. Contact C21 development team

---

**Migration Version**: 19.0.2.0.0
**Last Updated**: April 2026
