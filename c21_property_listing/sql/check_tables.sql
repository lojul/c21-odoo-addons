-- =====================================================
-- C21 Property Listing - Database Verification Queries
-- Run these after module installation to verify tables
-- =====================================================

-- =====================================================
-- 1. CHECK IF TABLES EXIST
-- =====================================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'c21_%'
ORDER BY table_name;

-- =====================================================
-- 2. TABLE: c21_property_listing (Main Properties)
-- =====================================================

-- Check table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'c21_property_listing'
ORDER BY ordinal_position;

-- Count records
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE listing_type = 'coworking') as coworking,
    COUNT(*) FILTER (WHERE listing_type = 'leasing') as leasing
FROM c21_property_listing;

-- Sample data
SELECT
    id,
    ref_code,
    name,
    listing_type,
    district,
    state,
    approval_status,
    CASE
        WHEN listing_type = 'coworking' THEN capacity::text || ' pax'
        ELSE net_area::text || ' sqft'
    END as size_display,
    CASE
        WHEN listing_type = 'coworking' THEN COALESCE(office_price, hot_desk_price, dedicated_desk_price)
        ELSE asking_rent
    END as price,
    create_date
FROM c21_property_listing
ORDER BY create_date DESC
LIMIT 20;

-- =====================================================
-- 3. TABLE: c21_property_image (Property Images)
-- =====================================================

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'c21_property_image'
ORDER BY ordinal_position;

-- Count images per property
SELECT
    p.ref_code,
    p.name,
    COUNT(i.id) as image_count
FROM c21_property_listing p
LEFT JOIN c21_property_image i ON i.property_id = p.id
GROUP BY p.id, p.ref_code, p.name
ORDER BY image_count DESC
LIMIT 20;

-- Sample images
SELECT
    i.id,
    p.ref_code,
    i.name as image_name,
    i.image_url,
    i.is_cover,
    i.sequence
FROM c21_property_image i
JOIN c21_property_listing p ON p.id = i.property_id
ORDER BY p.ref_code, i.sequence
LIMIT 20;

-- =====================================================
-- 4. TABLE: c21_property_amenity (Amenities Master)
-- =====================================================

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'c21_property_amenity'
ORDER BY ordinal_position;

-- All amenities
SELECT
    id,
    code,
    name,
    name_cn,
    category,
    icon,
    active
FROM c21_property_amenity
ORDER BY category, name;

-- Count by category
SELECT
    category,
    COUNT(*) as count
FROM c21_property_amenity
WHERE active = true
GROUP BY category;

-- =====================================================
-- 5. TABLE: c21_property_contact (Property Contacts)
-- =====================================================

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'c21_property_contact'
ORDER BY ordinal_position;

-- Contacts with property and partner info
SELECT
    c.id,
    p.ref_code,
    p.name as property_name,
    rp.name as contact_name,
    c.role,
    c.is_primary,
    rp.email,
    rp.phone
FROM c21_property_contact c
JOIN c21_property_listing p ON p.id = c.property_id
JOIN res_partner rp ON rp.id = c.partner_id
ORDER BY p.ref_code, c.sequence
LIMIT 20;

-- =====================================================
-- 6. TABLE: c21_property_listing_amenity_rel (M2M)
-- =====================================================

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'c21_property_listing_amenity_rel'
ORDER BY ordinal_position;

-- Properties with their amenities
SELECT
    p.ref_code,
    p.name,
    STRING_AGG(a.code, ', ' ORDER BY a.name) as amenities
FROM c21_property_listing p
JOIN c21_property_listing_amenity_rel rel ON rel.c21_property_listing_id = p.id
JOIN c21_property_amenity a ON a.id = rel.c21_property_amenity_id
GROUP BY p.id, p.ref_code, p.name
LIMIT 20;

-- =====================================================
-- 7. TABLE: res_partner (Extended - Operators)
-- =====================================================

-- Check new columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'res_partner'
  AND column_name IN ('is_property_operator', 'operator_logo_url')
ORDER BY column_name;

-- List operators
SELECT
    id,
    name,
    email,
    phone,
    is_property_operator,
    operator_logo_url
FROM res_partner
WHERE is_property_operator = true
ORDER BY name;

-- Operators with property count
SELECT
    rp.id,
    rp.name as operator_name,
    rp.email,
    COUNT(p.id) as property_count
FROM res_partner rp
LEFT JOIN c21_property_listing p ON p.operator_id = rp.id
WHERE rp.is_property_operator = true
GROUP BY rp.id, rp.name, rp.email
ORDER BY property_count DESC;

-- =====================================================
-- 8. SUMMARY STATISTICS
-- =====================================================

SELECT
    'c21_property_listing' as table_name,
    COUNT(*) as row_count
FROM c21_property_listing
UNION ALL
SELECT
    'c21_property_image',
    COUNT(*)
FROM c21_property_image
UNION ALL
SELECT
    'c21_property_amenity',
    COUNT(*)
FROM c21_property_amenity
UNION ALL
SELECT
    'c21_property_contact',
    COUNT(*)
FROM c21_property_contact
UNION ALL
SELECT
    'c21_property_listing_amenity_rel',
    COUNT(*)
FROM c21_property_listing_amenity_rel
UNION ALL
SELECT
    'res_partner (operators)',
    COUNT(*)
FROM res_partner
WHERE is_property_operator = true;

-- =====================================================
-- 9. DISTRICT STATISTICS (After data import)
-- =====================================================

SELECT
    district,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE listing_type = 'coworking') as coworking,
    COUNT(*) FILTER (WHERE listing_type = 'leasing') as leasing,
    COUNT(*) FILTER (WHERE state = 'available') as available
FROM c21_property_listing
GROUP BY district
ORDER BY total DESC;

-- =====================================================
-- 10. APPROVAL STATUS OVERVIEW
-- =====================================================

SELECT
    approval_status,
    listing_type,
    COUNT(*) as count
FROM c21_property_listing
GROUP BY approval_status, listing_type
ORDER BY approval_status, listing_type;
