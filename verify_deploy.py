#!/usr/bin/env python3
"""Verify c21 modules are properly deployed on Railway"""
import os
import sys

# Check all possible addons paths
PATHS = [
    "/mnt/extra-addons/c21_property_listing",
    "/var/lib/odoo/addons/19.0/c21_property_listing",
    "/usr/lib/python3/dist-packages/addons/c21_property_listing"
]

print("Checking c21_property_listing deployment...\n")

for path in PATHS:
    if os.path.exists(path):
        print(f"✅ Found module at: {path}")
        views_path = os.path.join(path, "views")
        if os.path.exists(views_path):
            views = os.listdir(views_path)
            print(f"   Views folder contains {len(views)} files:")
            for v in sorted(views):
                print(f"     - {v}")

            # Check for property_image_views.xml
            if "property_image_views.xml" in views:
                print(f"\n   ✅ property_image_views.xml EXISTS!")
            else:
                print(f"\n   ❌ property_image_views.xml MISSING!")
        print()
    else:
        print(f"❌ Not found: {path}")

print("\nDone!")
