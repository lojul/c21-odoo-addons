#!/usr/bin/env python3
"""
Test script for Odoo Property Listing API

Usage:
    python test_property_api.py

Before running:
1. Create an API key in Odoo: Settings → Users → Your User → Preferences → API Keys
2. Update the API_KEY variable below with your key
"""

import xmlrpc.client
import sys

# =============================================================================
# CONFIGURATION - Update these values
# =============================================================================
URL = "https://188.166.189.244.nip.io"
DB = "odoo"
USERNAME = "admin"  # Your Odoo login (not email)
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your API key from Odoo Preferences

# =============================================================================
# API Connection
# =============================================================================

def connect():
    """Authenticate and return uid and models proxy."""
    print(f"Connecting to {URL}...")

    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")

    # Test server is reachable
    version = common.version()
    print(f"✓ Server version: {version['server_version']}")

    # Authenticate
    uid = common.authenticate(DB, USERNAME, API_KEY, {})
    if not uid:
        print("✗ Authentication failed! Check your username and API key.")
        sys.exit(1)

    print(f"✓ Authenticated as user ID: {uid}")

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    return uid, models


def test_read(uid, models):
    """Test READ operations."""
    print("\n" + "="*50)
    print("TEST: READ Property Listings")
    print("="*50)

    # Search for all property listings
    ids = models.execute_kw(
        DB, uid, API_KEY,
        'c21.property.listing', 'search',
        [[]],  # Empty domain = all records
        {'limit': 5}
    )
    print(f"✓ Found {len(ids)} listings (showing max 5)")

    if ids:
        # Read specific fields
        records = models.execute_kw(
            DB, uid, API_KEY,
            'c21.property.listing', 'read',
            [ids],
            {'fields': ['ref_code', 'name', 'district', 'state', 'listing_type', 'asking_rent']}
        )

        print("\nProperty Listings:")
        print("-" * 80)
        for r in records:
            rent = f"${r['asking_rent']:,.0f}" if r['asking_rent'] else "N/A"
            print(f"  [{r['ref_code']}] {r['name'][:30]:<30} | {r['district']:<15} | {r['state']:<12} | {rent}")

    return ids


def test_search_read(uid, models):
    """Test search_read (combined search + read)."""
    print("\n" + "="*50)
    print("TEST: SEARCH_READ (Available Leasing Properties)")
    print("="*50)

    records = models.execute_kw(
        DB, uid, API_KEY,
        'c21.property.listing', 'search_read',
        [[
            ['state', '=', 'available'],
            ['listing_type', '=', 'leasing']
        ]],
        {
            'fields': ['ref_code', 'name', 'district', 'asking_rent'],
            'limit': 5,
            'order': 'asking_rent desc'
        }
    )

    print(f"✓ Found {len(records)} available leasing properties")
    for r in records:
        rent = f"${r['asking_rent']:,.0f}" if r['asking_rent'] else "N/A"
        print(f"  [{r['ref_code']}] {r['name'][:40]:<40} | {rent}")

    return records


def test_create(uid, models):
    """Test CREATE operation."""
    print("\n" + "="*50)
    print("TEST: CREATE New Property Listing")
    print("="*50)

    new_record = {
        'ref_code': 'API-TEST-001',
        'name': 'API Test Property',
        'name_cn': 'API 測試物業',
        'listing_type': 'leasing',
        'district': 'central',
        'property_type': 'office',
        'building_name': 'Test Building',
        'address': '123 Test Street',
        'floor': '10',
        'gross_area': 1000,
        'net_area': 800,
        'asking_rent': 50000,
        'state': 'available',
        'approval_status': 'draft',
    }

    try:
        new_id = models.execute_kw(
            DB, uid, API_KEY,
            'c21.property.listing', 'create',
            [new_record]
        )
        print(f"✓ Created new property with ID: {new_id}")
        return new_id
    except Exception as e:
        print(f"✗ Create failed: {e}")
        return None


def test_update(uid, models, record_id):
    """Test UPDATE operation."""
    print("\n" + "="*50)
    print(f"TEST: UPDATE Property ID {record_id}")
    print("="*50)

    try:
        result = models.execute_kw(
            DB, uid, API_KEY,
            'c21.property.listing', 'write',
            [[record_id], {
                'name': 'API Test Property (Updated)',
                'asking_rent': 55000,
                'state': 'under_negotiation',
            }]
        )
        print(f"✓ Updated successfully: {result}")

        # Verify the update
        updated = models.execute_kw(
            DB, uid, API_KEY,
            'c21.property.listing', 'read',
            [[record_id]],
            {'fields': ['name', 'asking_rent', 'state']}
        )
        print(f"  New values: {updated[0]}")
        return True
    except Exception as e:
        print(f"✗ Update failed: {e}")
        return False


def test_delete(uid, models, record_id):
    """Test DELETE operation."""
    print("\n" + "="*50)
    print(f"TEST: DELETE Property ID {record_id}")
    print("="*50)

    try:
        result = models.execute_kw(
            DB, uid, API_KEY,
            'c21.property.listing', 'unlink',
            [[record_id]]
        )
        print(f"✓ Deleted successfully: {result}")
        return True
    except Exception as e:
        print(f"✗ Delete failed: {e}")
        print("  (Note: Delete requires Property Manager role)")
        return False


def test_count(uid, models):
    """Test counting records."""
    print("\n" + "="*50)
    print("TEST: COUNT Records")
    print("="*50)

    total = models.execute_kw(
        DB, uid, API_KEY,
        'c21.property.listing', 'search_count',
        [[]]
    )

    available = models.execute_kw(
        DB, uid, API_KEY,
        'c21.property.listing', 'search_count',
        [[['state', '=', 'available']]]
    )

    coworking = models.execute_kw(
        DB, uid, API_KEY,
        'c21.property.listing', 'search_count',
        [[['listing_type', '=', 'coworking']]]
    )

    print(f"  Total listings:     {total}")
    print(f"  Available:          {available}")
    print(f"  Co-working spaces:  {coworking}")


def main():
    print("="*50)
    print("ODOO PROPERTY LISTING API TEST")
    print("="*50)

    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  Please update API_KEY in this script first!")
        print("   1. Login to Odoo")
        print("   2. Go to Settings → Users → Your User → Preferences")
        print("   3. Click 'New API Key' under API Keys section")
        print("   4. Copy the key and paste it in this script")
        sys.exit(1)

    # Connect
    uid, models = connect()

    # Test READ
    test_read(uid, models)
    test_search_read(uid, models)
    test_count(uid, models)

    # Test CREATE
    new_id = test_create(uid, models)

    if new_id:
        # Test UPDATE
        test_update(uid, models, new_id)

        # Test DELETE
        test_delete(uid, models, new_id)

    print("\n" + "="*50)
    print("API TEST COMPLETE")
    print("="*50)


if __name__ == "__main__":
    main()
