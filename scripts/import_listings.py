#!/usr/bin/env python3
"""
Import property listings from CSV to Odoo
"""
import csv
import re
import xmlrpc.client
from datetime import datetime

# Odoo connection
URL = "https://188.166.189.244.nip.io"
DB = "odoo"
USERNAME = "admin"
API_KEY = "44e48be869fa7e07c2348c092f549ba8ab657cc9"

# District mapping (Chinese -> code)
DISTRICT_MAP = {
    '中環': 'central',
    '金鐘': 'admiralty',
    '灣仔': 'wan_chai',
    '銅鑼灣': 'causeway_bay',
    '北角': 'north_point',
    '鰂魚涌': 'quarry_bay',
    '太古': 'taikoo',
    '黃竹坑': 'wong_chuk_hang',
    '上環': 'sheung_wan',
    '西營盤': 'sai_ying_pun',
    '尖沙咀': 'tsim_sha_tsui',
    '佐敦': 'jordan',
    '旺角': 'mong_kok',
    '九龍灣': 'kowloon_bay',
    '觀塘': 'kwun_tong',
    '新蒲崗': 'san_po_kong',
    '長沙灣': 'cheung_sha_wan',
    '深水埗': 'sham_shui_po',
    '黃埔': 'whampoa',
    '葵涌': 'kwai_chung',
    '荃灣': 'tsuen_wan',
    '沙田': 'sha_tin',
    '火炭': 'fo_tan',
    '屯門': 'tuen_mun',
    '元朗': 'yuen_long',
    '寶琳': 'po_lam',
    '大埔': 'tai_po',
    '匡湖居': 'other',  # Specific development, map to other
}

# Property type mapping
PROP_TYPE_MAP = {
    'Office': 'office',
    'Retail': 'retail',
    'Industrial': 'industrial',
}


def parse_rent(value):
    """Parse rent value like '$69,000' or '$10.476萬' to float"""
    if not value or not value.strip():
        return 0.0

    value = value.strip()

    # Remove $ sign
    value = value.replace('$', '').replace(',', '').strip()

    # Check if it's in 萬 (10k)
    if '萬' in value:
        value = value.replace('萬', '').strip()
        try:
            return float(value) * 10000
        except:
            return 0.0

    # Regular number
    try:
        return float(value)
    except:
        return 0.0


def parse_area(value):
    """Parse area value like '4,041' to float"""
    if not value or not value.strip():
        return 0.0

    value = value.replace(',', '').strip()
    try:
        return float(value)
    except:
        return 0.0


def parse_date(value):
    """Parse date like '24/4/2026' to 'YYYY-MM-DD'"""
    if not value or not value.strip():
        return False

    try:
        # Try DD/MM/YYYY format
        dt = datetime.strptime(value.strip(), '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return False


def generate_ref_code(index):
    """Generate ref code like LS-0001"""
    return f"LS-{index:04d}"


def main():
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USERNAME, API_KEY, {})

    if not uid:
        print("Authentication failed!")
        return

    print(f"Authenticated as user {uid}")

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    # Get source_id for SPP
    source_ids = models.execute_kw(DB, uid, API_KEY,
        'c21.property.source', 'search',
        [[['code', '=', 'spp']]])

    if not source_ids:
        # Create SPP source if not exists
        print("Creating SPP source...")
        source_id = models.execute_kw(DB, uid, API_KEY,
            'c21.property.source', 'create',
            [{'name': 'SPP', 'name_cn': 'SPP', 'code': 'spp'}])
    else:
        source_id = source_ids[0]

    print(f"Using source_id: {source_id}")

    # Get property type IDs
    prop_types = models.execute_kw(DB, uid, API_KEY,
        'c21.property.type', 'search_read',
        [[]], {'fields': ['id', 'code']})
    prop_type_map = {pt['code']: pt['id'] for pt in prop_types}
    print(f"Property types: {prop_type_map}")

    # Read CSV
    csv_path = "/Users/kincheonglau/Claude Cowork/odoo19/data import/listings_v5_modified.csv"

    created = 0
    skipped = 0
    errors = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for index, row in enumerate(reader, start=1):
            try:
                # Get Chinese name (required)
                name_cn = row.get('Chinese Name / 中文名稱', '').strip()
                if not name_cn:
                    skipped += 1
                    continue

                # English name - use Chinese if empty
                name = row.get('English Name / 英文名稱', '').strip()
                if not name:
                    name = name_cn

                # District
                district_cn = row.get('District / 地區', '').strip()
                district = DISTRICT_MAP.get(district_cn, 'other')

                # Property type
                prop_type_str = row.get('Prop Type / 用途', '').strip()
                prop_type_code = PROP_TYPE_MAP.get(prop_type_str, 'retail')
                property_type_id = prop_type_map.get(prop_type_code)

                # Parse numeric fields
                gross_area = parse_area(row.get('Gross sqft / 建呎', ''))
                net_area = parse_area(row.get('Total Area / 總面積', ''))
                asking_rent = parse_rent(row.get('Rent / 租價', ''))

                # Parse dates
                followup_date = parse_date(row.get('Follow-up / 跟進日期', ''))

                # Build record
                vals = {
                    'name': name,
                    'name_cn': name_cn,
                    'ref_code': generate_ref_code(index),
                    'listing_type': 'leasing',
                    'approval_status': 'draft',
                    'district': district,
                    'address': row.get('Street / 街道', '').strip(),
                    'building_name': row.get('Building / 物業名稱', '').strip(),
                    'floor': row.get('Floor / 樓層', '').strip(),
                    'unit': row.get('Unit / 室號', '').strip(),
                    'property_type_id': property_type_id,
                    'gross_area': gross_area,
                    'net_area': net_area if net_area else gross_area,
                    'asking_rent': asking_rent,
                    'year_built': row.get('Year Built / 樓齡', '').strip(),
                    'internal_notes': row.get('Internal Notes / 提示', '').strip(),
                    'source_id': source_id,
                }

                if followup_date:
                    vals['followup_date'] = followup_date

                # Create record
                record_id = models.execute_kw(DB, uid, API_KEY,
                    'c21.property.listing', 'create', [vals])

                created += 1
                print(f"Created: {name_cn} (ID: {record_id})")

            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                print(f"Error on row {index}: {e}")

    print(f"\n=== Import Complete ===")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors[:10]:
            print(f"  - {err}")


if __name__ == '__main__':
    main()
