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

### c21_social_marketing (Application)
- Automated social media posts for HK property news
- Location: `/addons/c21_social_marketing/`

#### Key Features
- RSS news scraping from Google News, SCMP, etc.
- AI caption generation (DeepSeek via OpenRouter)
- Image generation with PIL
- Buffer API integration for FB/IG/Threads

#### RSS Scraper (`utils/rss_scraper.py`)
- **Date filtering**: Only fetches news from last 30 days
- **Future date skip**: Skips items with invalid future dates
- **Duplicate check**: Skips URLs already in database
- **Auto-cleanup**: Removes old news after each fetch

#### Cleanup Criteria
- **Old news**: `fetch_date` > 7 days AND `used = False`
- **Invalid news**: `publish_date` in future AND `used = False`
- News marked as `used = True` (turned into posts) are never deleted

#### Manual Cleanup
- Menu: C21 Social Marketing → 清理舊新聞
- Or via shell: `env['c21.social.news'].action_cleanup_all()`

#### Cron Jobs
- Fetch news: Every hour
- Generate posts: 9am, 1pm, 5pm HKT
- Cleanup old news: Weekly

#### Deployment
```bash
./scripts/deploy_social_marketing.sh
```
Or manually:
```bash
rsync -avz addons/c21_social_marketing/ root@188.166.189.244:/opt/odoo/addons/c21_social_marketing/
ssh root@188.166.189.244 "cd /opt/odoo && docker compose exec -T odoo odoo -d odoo --db_host=db --db_user=odoo --db_password=odoo_secure_pw_2024 -u c21_social_marketing --stop-after-init"
ssh root@188.166.189.244 "cd /opt/odoo && docker compose restart odoo"
```

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

### Server Info
- **Host**: `root@188.166.189.244` (Digital Ocean)
- **Odoo Path**: `/opt/odoo`
- **DB**: PostgreSQL in Docker (`db` container)
- **DB Credentials**: `odoo` / `odoo_secure_pw_2024`

### Quick Deploy (Social Marketing)
```bash
./scripts/deploy_social_marketing.sh
```

### Manual Deploy
1. Copy files to server:
   ```bash
   rsync -avz --delete addons/MODULE_NAME/ root@188.166.189.244:/opt/odoo/addons/MODULE_NAME/
   ```

2. Upgrade module:
   ```bash
   ssh root@188.166.189.244 "cd /opt/odoo && docker compose exec -T odoo odoo -d odoo --db_host=db --db_user=odoo --db_password=odoo_secure_pw_2024 -u MODULE_NAME --stop-after-init"
   ```

3. Restart Odoo:
   ```bash
   ssh root@188.166.189.244 "cd /opt/odoo && docker compose restart odoo"
   ```

### Odoo Shell (for debugging)
```bash
ssh root@188.166.189.244 "cd /opt/odoo && docker compose exec -T odoo odoo shell -d odoo --db_host=db --db_user=odoo --db_password=odoo_secure_pw_2024 --no-http"
```

### Docker Notes
- Dockerfile requires `--break-system-packages` for pip (Python 3.12)
- Location: `docker/Dockerfile`

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

## n8n Workflows

### Location
- Workflow files: `/n8n/`
- Triggered by: OneDrive folder watch

### Property Document Processor v1.2.1 (List Support Fixed)
- **File**: `n8n/Property Document Processor v1.2-list.json`
- **Purpose**: Process PDFs from OneDrive, extract property data, upload to Odoo
- **Supports**: Single property PDFs, bulk listing tables (旺舖出租精選), images

#### Document Types
| Type | Ref Code Prefix | Example |
|------|-----------------|---------|
| Single listing PDF | `PROP-YYYYMMDD-XXX` | Individual property documents |
| Bulk list PDF | `MB-XXXXXX` | Table with multiple properties (樓盤編號) |
| Manual import | `SPP-XXXXX`, `LS-XXXX` | CSV/manual imports |

#### Key Nodes for List Processing
```
Split Into Items → Loop List Items → Map to Schema → Index Azure → Odoo Upsert
                        ↑                                              ↓
                        └──────────────────────────────────────────────┘
```

#### Troubleshooting
- **Only 1 item processed**: Check "Loop List Items" node exists after "Split Into Items"
- **No items created**: Check AI Classification output
- **Images missing**: List PDFs don't contain photos; need separate image files

#### Config Node
The "Config (API Keys)" node contains placeholders - update with actual keys:
- `AZURE_DOC_INTEL_KEY` - Azure Document Intelligence
- `AZURE_OPENAI_KEY` - Azure OpenAI for embeddings
- `AZURE_SEARCH_API_KEY` - Azure AI Search
- `ODOO_API_KEY` - Odoo JSON-RPC API key

### Fix History
- **v1.2.1** (2026-05-06): Added missing `Loop List Items` (SplitInBatches) node to iterate through all extracted list items. Previously only processed first item.

### Future: LangGraph Migration
Consider migrating from n8n to LangGraph for:
- **Better debugging** - Python stack traces, breakpoints, unit tests
- **Cleaner code** - Python files vs JS embedded in JSON
- **Testability** - Unit test each node independently
- **State management** - First-class support for workflow state

Migration approach:
1. Keep n8n for simple triggers only
2. n8n calls LangGraph API endpoint for processing
3. Or replace entirely with Python script + cron/webhook

### Alternative Triggers (Better than OneDrive)
| Method | Pros | Cons |
|--------|------|------|
| **WhatsApp Bot** | Agents already use WhatsApp; send PDF via chat | Need WhatsApp Business API |
| **Odoo Upload** | Most integrated; upload in property form | Need custom Odoo module |
| **Web Form** | Simple HTML upload page | Need to host/secure |
| **Email** | Send PDF as attachment | Parsing attachments |
| **Telegram Bot** | Free, easy API | Less common in HK |
| **S3/Azure Blob Watch** | More reliable than OneDrive | More setup |

**Recommended**: WhatsApp or Odoo built-in upload for best UX.

## Documentation Files
- `WORK_SUMMARY.md` - Detailed work history and procedures
- `CHANGELOG_v2.md` - Version changelog
- `LAYOUT_GUIDELINES.md` - UI/UX guidelines
