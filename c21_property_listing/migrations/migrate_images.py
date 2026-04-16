#!/usr/bin/env python3
"""
Migration script to download images from URLs to Image fields.
Can be run from Odoo shell or as a standalone script.

Usage from Odoo shell:
    from c21_property_listing.migrations.migrate_images import migrate_all_images
    migrate_all_images(env)

Or run as shell command:
    odoo shell -d your_database --addons-path=/path/to/addons -c /path/to/odoo.conf
    >>> from c21_property_listing.migrations.migrate_images import migrate_all_images
    >>> migrate_all_images(env)
"""

import logging

_logger = logging.getLogger(__name__)


def migrate_all_images(env):
    """Download all images from URLs that don't have image data yet"""
    PropertyImage = env['c21.property.image']

    # Find all records with URL but no image data
    images_to_migrate = PropertyImage.search([
        ('image_url', '!=', False),
        ('image', '=', False)
    ])

    total = len(images_to_migrate)
    if total == 0:
        _logger.info("No images to migrate. All images already downloaded.")
        return {'success': 0, 'failed': 0, 'total': 0}

    _logger.info(f"Starting migration for {total} images...")

    success_count = 0
    failed_count = 0

    for idx, img in enumerate(images_to_migrate, 1):
        try:
            _logger.info(f"[{idx}/{total}] Downloading: {img.image_url}")
            image_data = img._download_image_from_url(img.image_url)

            if image_data:
                img.image = image_data
                success_count += 1
                _logger.info(f"  ✓ Success")
            else:
                failed_count += 1
                _logger.warning(f"  ✗ Failed to download")

        except Exception as e:
            failed_count += 1
            _logger.error(f"  ✗ Error: {str(e)}")

        # Commit every 10 images to avoid memory issues
        if idx % 10 == 0:
            env.cr.commit()
            _logger.info(f"Progress: {idx}/{total} ({success_count} success, {failed_count} failed)")

    # Final commit
    env.cr.commit()

    _logger.info(f"Migration complete: {success_count} success, {failed_count} failed out of {total} total")

    return {
        'success': success_count,
        'failed': failed_count,
        'total': total
    }


def migrate_property_images(env, property_ids):
    """Download images for specific properties"""
    PropertyImage = env['c21.property.image']

    images_to_migrate = PropertyImage.search([
        ('property_id', 'in', property_ids),
        ('image_url', '!=', False),
        ('image', '=', False)
    ])

    total = len(images_to_migrate)
    _logger.info(f"Migrating {total} images for {len(property_ids)} properties...")

    success_count = 0
    failed_count = 0

    for img in images_to_migrate:
        try:
            image_data = img._download_image_from_url(img.image_url)
            if image_data:
                img.image = image_data
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            _logger.error(f"Error downloading image {img.id}: {str(e)}")

    env.cr.commit()

    return {
        'success': success_count,
        'failed': failed_count,
        'total': total
    }
