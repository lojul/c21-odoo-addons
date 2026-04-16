# Changelog - Version 2.0.0

## 🎉 Major Update: Image Storage System

**Version**: 19.0.2.0.0
**Date**: April 16, 2026
**Type**: Major Feature Enhancement

### 📸 Image Storage Overhaul

#### What's New

**Store Actual Images Instead of URLs**
- Images now stored directly in Odoo database
- Automatic image resizing (full, medium 512x512, small 256x256)
- Better performance and offline access
- No dependency on external CDN for viewing

**Auto-Download from URLs**
- Paste image URL → automatic download
- Legacy `image_url` field triggers auto-download on save
- Manual download button available per image
- Bulk download action for multiple properties

**New Views**
- Image Gallery (Kanban view) - Visual browsing of all images
- Enhanced List View - Thumbnail previews
- Detailed Form View - Full image management

**Migration Tools**
- Migration script: `migrations/migrate_images.py`
- Server actions for bulk download
- Automatic download on create/update with URL

### 🔧 Technical Changes

#### Modified Files

**Models**
- `models/property_image.py` - Added Image fields, auto-download logic

**Views**
- `views/property_listing_views.xml` - Updated Images tab with preview
- `views/property_image_views.xml` - NEW: Form/List/Kanban views for images
- `views/menu.xml` - Added "All Images" menu item

**Data**
- `data/server_actions.xml` - Added image download actions

**Configuration**
- `__manifest__.py` - Version bump to 2.0.0, added `requests` dependency

**Documentation**
- `IMAGE_MIGRATION_GUIDE.md` - Complete migration instructions
- `CHANGELOG_v2.md` - This file

#### New Fields

```python
# Property Image Model
image = fields.Image()              # Full size (max 1920x1920)
image_medium = fields.Image()       # 512x512
image_small = fields.Image()        # 256x256

# Legacy fields (kept for migration)
image_url = fields.Char()           # Triggers auto-download
thumbnail_url = fields.Char()       # Reference only
```

#### Database Changes

**New Columns**
- `c21_property_image.image` (bytea)
- `c21_property_image.image_medium` (bytea)
- `c21_property_image.image_small` (bytea)

**Modified Columns**
- `c21_property_image.image_url` - No longer required
- `c21_property_image.thumbnail_url` - No longer required

### 📦 Dependencies

**New Python Dependency**
- `requests` - For downloading images from URLs

Install if not present:
```bash
pip3 install requests
```

### 🚀 Upgrade Path

1. **Backup your database**
2. **Update the module code** (git pull / Railway deploy)
3. **Upgrade module in Odoo** (Apps → C21 → Upgrade)
4. **Migrate existing images** (see IMAGE_MIGRATION_GUIDE.md)

### 📊 Migration Options

**Option 1: Automatic (Passive)**
- Images download automatically when records are saved
- Happens naturally over time

**Option 2: Bulk UI Action (Recommended)**
- Select properties → Action → "Download Images from URLs"
- Immediate migration with progress notification

**Option 3: Python Script (Advanced)**
```python
from c21_property_listing.migrations.migrate_images import migrate_all_images
migrate_all_images(env)
```

### 🎯 Benefits

1. **Performance**
   - Faster image loading (no external CDN requests)
   - Automatic caching by Odoo
   - Reduced external dependencies

2. **Offline Access**
   - Images viewable without internet
   - Works in disconnected environments

3. **Image Management**
   - Automatic resizing for different contexts
   - Consistent image quality
   - Better mobile experience

4. **Data Ownership**
   - Images stored in your database
   - Full control over image data
   - Database backups include images

### ⚠️ Considerations

**Database Size**
- Images increase database size
- ~200KB per full image (compressed)
- Three sizes per image (full, medium, small)

**Railway Deployment**
- Monitor database size on Railway
- Consider storage limits in your plan
- Database backups will be larger

### 🔄 Backward Compatibility

**Legacy URL Fields**
- Still available but hidden
- Used for migration trigger
- Will be removed in v20.0

**Existing Functionality**
- All existing features work unchanged
- No breaking changes to API (Phase 3)
- Forms and views remain compatible

### 🐛 Known Issues

None at this time.

### 📝 Notes

- Legacy `image_url` and `thumbnail_url` fields are retained for migration
- Server actions available for bulk operations
- Full migration guide available in `IMAGE_MIGRATION_GUIDE.md`

### 🙏 Credits

Feature developed for C21 Property Management system to improve user experience and system performance.

---

**Next Version Preview (v19.0.2.1.0)**
- Image compression optimization
- Bulk upload UI
- Image metadata extraction
