# Claude Code Memory - C21 Odoo Project

## Project Overview

- **Platform**: Odoo 19 on Railway (Docker)
- **Server URL**: http://188.166.189.244.nip.io/odoo
- **Repository**: https://github.com/lojul/c21-odoo-addons.git
- **Main Branch**: main

## Key Modules

### c21_property_listing (Application)
- Main property management module
- Handles co-working spaces and leasing properties
- Bilingual support (English/Chinese)
- Location: `/c21_property_listing/`

### c21_property_reports (Add-on)
- PDF report generation for properties
- Property Particulars report (single property)
- Property Comparison report (2-5 properties)
- Location: `/addons/c21_property_reports/`

## Report System

### Template Files
- `addons/c21_property_reports/report/property_report_templates.xml` - QWeb HTML templates
- `addons/c21_property_reports/static/src/css/report.css` - Report styling
- `addons/c21_property_reports/report/property_report.py` - Data processing

### How to Print Reports
1. **Property Particulars**: Form view → Print button (or Action → Print menu)
2. **Property Comparison**: List view → Select 2-5 properties → Action → Compare Properties

### Editing Templates in UI
1. Enable Developer Mode: `?debug=1` in URL
2. Settings → Technical → User Interface → Views
3. Search for template name (e.g., `report_property_particulars`)

## Chatter Toggle Feature
- Toggle button to hide/show activity panel on property form
- JS file: `c21_property_listing/static/src/js/chatter_toggle.js`
- CSS file: `c21_property_listing/static/src/css/chatter_toggle.css`
- State persisted in localStorage

## Deployment Flow

1. Commit and push to GitHub
2. On Railway server:
   ```bash
   git pull origin main
   docker-compose down && docker-compose up -d --build
   ```
3. In Odoo UI: Apps → Upgrade modules

## Common Tasks

### Add new field to report
Edit `property_report_templates.xml`:
```xml
<tr t-if="doc.your_field">
    <td class="c21-label">Label / 中文</td>
    <td class="c21-value"><t t-esc="doc.your_field"/></td>
</tr>
```

### Add button to form via inheritance
Create view inheritance XML with xpath:
```xml
<xpath expr="//div[@name='button_box']" position="inside">
    <button name="action_method" type="object" class="oe_stat_button" icon="fa-icon"/>
</xpath>
```

## Documentation Files
- `WORK_SUMMARY.md` - Detailed work history and procedures
- `CHANGELOG_v2.md` - Version changelog
- `LAYOUT_GUIDELINES.md` - UI/UX guidelines
