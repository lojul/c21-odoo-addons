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
│ OVERVIEW                            │ IMAGES                    │
│ - Core identification fields        │ - Cover, Preview, Desc    │
│ - Status fields                     │                           │
│                                     │ CONTACT                   │
│ LOCATION                            │ - Name (linked), Title,   │
│ - Address fields                    │   Phone                   │
│                                     │                           │
│ DETAILS (conditional)               │                           │
│ - Type-specific fields              │                           │
│                                     │                           │
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

### Bilingual Format
Always use bilingual labels where applicable:
```xml
<field name="name" string="English Name / 英文名稱"/>
<field name="district" string="District / 地區"/>
```

### Label Styling
- Colons added automatically via CSS (except radio buttons)
- Fixed label width: 220px
- Font weight: 600
- Color: #374151

---

## Standard Sections

### 1. Overview Section
Core identification and status fields.

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
        <field name="type" widget="radio" options="{'horizontal': true}"/>
        <field name="status" string="Publish / 發佈"/>
        <field name="state"/>
    </group>
</group>
```

### 2. Location Section
Address and location fields.

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
        <!-- Hidden technical fields -->
        <field name="latitude" invisible="1"/>
        <field name="longitude" invisible="1"/>
    </group>
</group>
```

### 3. Conditional Details Section
Show/hide based on type selection.

```xml
<separator string="Type A Details" invisible="type != 'type_a'"/>
<group invisible="type != 'type_a'">
    <group>
        <!-- Type A specific fields -->
    </group>
    <group>
        <!-- More Type A fields -->
    </group>
</group>
```

### 4. Amenities/Tags Section
```xml
<separator string="Amenities"/>
<field name="amenity_ids" widget="many2many_tags"/>
```

### 5. Comment Section
Bilingual text areas.

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

### Images Section
```xml
<separator string="Images"/>
<field name="image_ids">
    <list editable="bottom">
        <field name="sequence" widget="handle"/>
        <field name="is_cover" string="Cover / 封面"/>
        <field name="image_small" widget="image" options="{'size': [64, 64]}" string="Preview / 預覽"/>
        <field name="name" string="Description / 描述"/>
    </list>
</field>
```

### Contact Section
Compact format with linked names.

```xml
<separator string="Contact"/>
<field name="contact_ids">
    <list editable="bottom">
        <field name="sequence" widget="handle"/>
        <field name="partner_id" string="Name / 姓名"/>
        <field name="role" string="Title / 職稱"/>
        <field name="phone" string="Phone / 電話"/>
    </list>
</field>
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

## Checklist for New Forms

- [ ] Apply `c21_property_form_aligned` class to form
- [ ] Use two-column layout with `c21_two_column_layout`
- [ ] Add bilingual labels (English / 中文)
- [ ] Use `<separator>` for section headers
- [ ] Place Images and Contact in side column
- [ ] Hide technical fields (lat/lng, currency_id, etc.)
- [ ] Use `invisible` attribute for conditional sections
- [ ] Add stat buttons for related records

---

## File References

- **CSS:** `c21_property_listing/static/src/css/operator_list.css`
- **Property Form:** `c21_property_listing/views/property_listing_views.xml`
- **Operator Form:** `c21_property_listing/views/property_operator_views.xml`
