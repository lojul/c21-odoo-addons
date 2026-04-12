-- C21 Property Listing - Quick Select Queries
-- Purpose: quick verification of new tables after module install

-- 1) c21_property_listing
SELECT
    id,
    ref_code,
    name,
    name_cn,
    listing_type,
    district,
    state,
    approval_status,
    operator_id,
    create_date,
    write_date
FROM c21_property_listing
ORDER BY write_date DESC NULLS LAST, create_date DESC NULLS LAST
LIMIT 100;

-- 2) c21_property_image
SELECT
    id,
    property_id,
    name,
    image_url,
    thumbnail_url,
    is_cover,
    sequence,
    create_date
FROM c21_property_image
ORDER BY property_id, sequence, id
LIMIT 200;

-- 3) c21_property_amenity
SELECT
    id,
    code,
    name,
    name_cn,
    category,
    icon,
    active,
    create_date
FROM c21_property_amenity
ORDER BY category, name;

-- 4) c21_property_contact
SELECT
    c.id,
    c.property_id,
    p.ref_code,
    p.name AS property_name,
    c.partner_id,
    rp.name AS contact_name,
    c.role,
    c.is_primary,
    c.sequence,
    rp.email,
    rp.phone,
    c.create_date
FROM c21_property_contact c
LEFT JOIN c21_property_listing p ON p.id = c.property_id
LEFT JOIN res_partner rp ON rp.id = c.partner_id
ORDER BY c.property_id, c.sequence, c.id
LIMIT 200;

-- 5) c21_property_listing_amenity_rel (M2M)
SELECT
    rel.c21_property_listing_id,
    p.ref_code,
    p.name AS property_name,
    rel.c21_property_amenity_id,
    a.code AS amenity_code,
    a.name AS amenity_name
FROM c21_property_listing_amenity_rel rel
LEFT JOIN c21_property_listing p ON p.id = rel.c21_property_listing_id
LEFT JOIN c21_property_amenity a ON a.id = rel.c21_property_amenity_id
ORDER BY rel.c21_property_listing_id, a.code
LIMIT 500;

-- 6) res_partner extension fields
SELECT
    id,
    name,
    email,
    phone,
    is_company,
    is_property_operator,
    operator_logo_url,
    create_date,
    write_date
FROM res_partner
WHERE is_property_operator = TRUE
ORDER BY name
LIMIT 200;
