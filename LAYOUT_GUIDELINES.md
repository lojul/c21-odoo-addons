# C21 Odoo Module Layout Guidelines

This document defines the standard layout patterns for C21 Odoo forms. Follow these guidelines for consistency across all modules.

---

## Form Structure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ Button Box (stat buttons: Images, Contacts, etc.)               │
├─────────────────────────────────────┬───────────────────────────┤
│ MAIN COLUMN (~65%)                  │ SIDE COLUMN (~35%)        │
├─────────────────────────────────────┼───────────────────────────┤
│ OVERVIEW                            │ IMAGES (card grid)        │
│ - English Name, Chinese Name,       │ ┌─────┐ ┌─────┐ ┌─────┐  │
│   Ref Code                          │ │ IMG │ │ IMG │ │ IMG │  │
│ - Type, Publish, Status             │ │Cover│ │     │ │     │  │
│                                     │ └─────┘ └─────┘ └─────┘  │
│ LOCATION                            │                           │
│ - Unit, Floor, Building,            │ CONTACT (card list)       │
│   Street, District                  │ ┌─────────────────────┐  │
│                                     │ │ 👤 Name      Primary│  │
│ DETAILS (conditional)               │ │    Title            │  │
│ - Co-working or Leasing fields      │ │ 📞 Phone            │  │
│                                     │ └─────────────────────┘  │
│ AMENITIES                           │                           │
│ - Tags                              │                           │
│                                     │                           │
│ COMMENT                             │                           │
│ - English text                      │                           │
│ - Chinese text                      │                           │
└─────────────────────────────────────┴───────────────────────────┘
```

---

## CSS Classes

### Form Container
```xml
<form string="Form Title" class="c21_property_form_aligned">
```

### Two-Column Layout
```xml
<div class="c21_two_column_layout">
    <div class="c21_main_column">
        <!-- Main content sections -->
    </div>
    <div class="c21_side_column">
        <!-- Supporting content: Images, Contacts -->
    </div>
</div>
```

---

## Section Headers

Use `<separator>` for section headers:
```xml
<separator string="Section Name"/>
```

### Styling (CSS)
- Font size: 16px
- Font weight: 700 (bold)
- Color: #714B67 (Odoo purple)
- Text transform: UPPERCASE
- Letter spacing: 0.5px
- Padding top: 16px
- Margin bottom: 8px

---

## Field Labels

### Bilingual Format with Colons
Always use bilingual labels with colons in dialog forms:
```xml
<field name="name" string="English Name / 英文名稱:"/>
<field name="district" string="District / 地區:"/>
<field name="is_primary" string="Primary Contact? / 主要聯絡人?"/>
```

### Label Styling
- Colons added automatically via CSS in main forms (except radio buttons)
- For dialog forms, add colons manually in string attribute
- Fixed label width: 220px
- Font weight: 600
- Color: #374151

---

## Standard Sections

### 1. Overview Section
Core identification and status fields in two columns.

```xml
<separator string="Overview"/>
<group>
    <group>
        <!-- Column 1: Identification -->
        <field name="name" string="English Name / 英文名稱"/>
        <field name="name_cn" string="Chinese Name / 中文名稱"/>
        <field name="ref_code"/>
    </group>
    <group>
        <!-- Column 2: Status -->
        <field name="listing_type" widget="radio" options="{'horizontal': true}"/>
        <field name="approval_status" string="Publish / 發佈"/>
        <field name="state"/>
    </group>
</group>
```

### 2. Location Section
Address fields in single column (hide lat/lng).

```xml
<separator string="Location"/>
<group>
    <group>
        <field name="unit"/>
        <field name="floor"/>
        <field name="building_name"/>
        <field name="address" string="Street / 街道"/>
        <field name="district"/>
    </group>
    <group>
        <field name="latitude" invisible="1"/>
        <field name="longitude" invisible="1"/>
    </group>
</group>
```

### 3. Conditional Details Section
Show/hide based on type selection.

```xml
<separator string="Co-working Details" invisible="listing_type != 'coworking'"/>
<group invisible="listing_type != 'coworking'">
    <group>
        <field name="operator_id"/>
        <field name="size"/>
        <field name="capacity"/>
        <field name="available_capacity"/>
    </group>
    <group>
        <field name="hot_desk_price"/>
        <field name="dedicated_desk_price"/>
        <field name="office_price"/>
    </group>
</group>
```

### 4. Amenities/Tags Section
```xml
<separator string="Amenities"/>
<field name="amenity_ids" widget="many2many_tags"/>
```

### 5. Comment Section
Bilingual text areas (renamed from Description).

```xml
<separator string="Comment"/>
<group>
    <field name="description" nolabel="1" placeholder="Comment in English..."/>
</group>
<group>
    <field name="description_cn" nolabel="1" placeholder="Comment in Chinese..."/>
</group>
```

---

## Side Column Components

### Images Section (Compact Cards)
Uses kanban view for card-style display.

```xml
<separator string="Images"/>
<field name="image_ids" class="c21_card_grid">
    <kanban class="c21_image_cards">
        <field name="id"/>
        <field name="is_cover"/>
        <field name="image_small"/>
        <field name="name"/>
        <templates>
            <t t-name="card" class="c21_image_card">
                <div class="c21_card_image">
                    <field name="image_small" widget="image" options="{'size': [60, 60]}"/>
                    <span t-if="record.is_cover.raw_value" class="c21_cover_badge">Cover</span>
                </div>
                <div class="c21_card_label" t-if="record.name.value">
                    <field name="name"/>
                </div>
            </t>
        </templates>
    </kanban>
</field>
```

### Contact Section (Compact Cards)
Uses kanban view for card-style display.

```xml
<separator string="Contact"/>
<field name="contact_ids" class="c21_card_grid">
    <kanban class="c21_contact_cards">
        <field name="id"/>
        <field name="partner_id"/>
        <field name="role"/>
        <field name="phone"/>
        <field name="is_primary"/>
        <templates>
            <t t-name="card" class="c21_contact_card">
                <div class="c21_contact_name">
                    <i class="fa fa-user me-1"/>
                    <field name="partner_id"/>
                    <span t-if="record.is_primary.raw_value" class="c21_primary_badge">Primary</span>
                </div>
                <div class="c21_contact_role" t-if="record.role.value">
                    <field name="role"/>
                </div>
                <div class="c21_contact_phone" t-if="record.phone.value">
                    <i class="fa fa-phone me-1"/>
                    <field name="phone"/>
                </div>
            </t>
        </templates>
    </kanban>
</field>
```

---

## Dialog Forms (Popup Windows)

### Contact Form Dialog
Two-column layout with proper field order.

```xml
<form string="Contact" class="c21_property_form_aligned">
    <sheet>
        <group>
            <group>
                <field name="property_id" string="Property / 物業:"/>
                <field name="partner_id" string="Name / 姓名:"/>
                <field name="role" string="Title / 職稱:"/>
                <field name="phone" string="Phone / 電話:"/>
                <field name="email" string="Email / 電郵:"/>
            </group>
            <group>
                <field name="is_primary" string="Primary Contact? / 主要聯絡人?"/>
                <field name="notes" string="Note / 備註:" placeholder="Additional notes..."/>
            </group>
        </group>
        <field name="sequence" invisible="1"/>
    </sheet>
</form>
```

### Image Form Dialog
Simplified layout with hidden technical fields.

```xml
<form string="Image" class="c21_property_form_aligned">
    <sheet>
        <group>
            <group>
                <field name="property_id" string="Property / 物業:"/>
                <field name="name" string="Description / 描述:" placeholder="Image description..."/>
                <field name="is_cover" string="Cover Image? / 封面圖?"/>
                <field name="image" widget="image" options="{'size': [0, 200]}"/>
            </group>
            <group>
                <button name="action_download_from_url" type="object"
                        string="Download" class="btn-primary"
                        invisible="not image_url"
                        icon="fa-download"/>
            </group>
        </group>
        <field name="sequence" invisible="1"/>
        <field name="image_url" invisible="1"/>
    </sheet>
</form>
```

---

## Side Column Styling

The right sidebar has subtle visual distinction:
- Background: #f8f9fa (light gray)
- Border: 1px solid #e9ecef
- Border radius: 8px
- Padding: 16px
- Min width: 320px
- Max width: 400px

---

## Card Styling

### Image Cards
```css
.c21_image_cards .o_kanban_record { width: 72px; }
.c21_image_card {
    background: #fff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 4px;
    text-align: center;
}
.c21_card_image img {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 4px;
}
.c21_cover_badge {
    position: absolute;
    top: 2px;
    right: 2px;
    background: #714B67;
    color: #fff;
    font-size: 9px;
    padding: 1px 4px;
    border-radius: 3px;
}
```

### Contact Cards
```css
.c21_contact_cards .o_kanban_record { width: 100%; }
.c21_contact_card {
    background: #fff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 10px 12px;
}
.c21_contact_name {
    font-weight: 600;
    color: #212529;
    font-size: 13px;
}
.c21_primary_badge {
    background: #198754;
    color: #fff;
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 3px;
}
.c21_contact_role {
    font-size: 12px;
    color: #6c757d;
}
.c21_contact_phone {
    font-size: 12px;
    color: #495057;
}
```

---

## Responsive Behavior

On screens < 1200px:
- Two-column layout stacks vertically
- Side column becomes full width

---

## Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Section headers | #714B67 | Odoo purple |
| Labels | #374151 | Dark gray |
| Label colons | #6b7280 | Medium gray |
| Side column bg | #f8f9fa | Light gray |
| Side column border | #e9ecef | Border gray |
| Cover badge | #714B67 | Odoo purple |
| Primary badge | #198754 | Bootstrap green |
| Card border | #dee2e6 | Light border |

---

## Radio Button Fields

Radio buttons should NOT have colons. CSS automatically suppresses them:
```css
.c21_property_form_aligned .o_radio_item label::after,
.c21_property_form_aligned .o_field_radio label::after {
    content: "" !important;
}
```

---

## Button Box (Stat Buttons)

Place at top of form for quick navigation:
```xml
<div class="oe_button_box" name="button_box">
    <button name="action_view_images" type="object"
            class="oe_stat_button" icon="fa-image">
        <field name="image_count" widget="statinfo" string="Images"/>
    </button>
    <button name="action_view_contacts" type="object"
            class="oe_stat_button" icon="fa-users">
        <field name="contact_count" widget="statinfo" string="Contacts"/>
    </button>
</div>
```

---

## Hiding Chatter (Conversation Panel)

To hide the chatter on inherited forms (like res.partner):

1. Add a marker class to the form:
```xml
<form position="attributes">
    <attribute name="class" add="c21_operator_form" separator=" "/>
</form>
```

2. Add CSS to hide chatter:
```css
.o_form_view:has(.c21_operator_form) .o-mail-ChatterContainer,
.o_form_view:has(.c21_operator_form) .o-mail-Chatter,
.o_form_view:has(.c21_operator_form) .oe_chatter {
    display: none !important;
}
```

---

## Checklist for New Forms

- [ ] Apply `c21_property_form_aligned` class to form
- [ ] Use two-column layout with `c21_two_column_layout`
- [ ] Add bilingual labels (English / 中文)
- [ ] Add colons to labels in dialog forms
- [ ] Use `<separator>` for section headers (UPPERCASE)
- [ ] Place Images and Contact in side column as card grids
- [ ] Hide technical fields (sequence, lat/lng, currency_id, URLs)
- [ ] Use `invisible` attribute for conditional sections
- [ ] Add stat buttons for related records
- [ ] Hide chatter if not needed (Operator form pattern)

---

## File References

- **CSS:** `c21_property_listing/static/src/css/operator_list.css`
- **Property Form:** `c21_property_listing/views/property_listing_views.xml`
- **Image/Contact Forms:** `c21_property_listing/views/property_image_views.xml`
- **Operator Form:** `c21_property_listing/views/property_operator_views.xml`
- **Menu:** `c21_property_listing/views/menu.xml`
