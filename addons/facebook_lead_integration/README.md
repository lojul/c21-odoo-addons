# Facebook Lead Integration - Odoo Module

Custom Odoo 19 module that extends CRM and Contacts to support Facebook lead capture via external integrations (n8n workflow).

## Purpose

This module adds Facebook-specific fields to Odoo's contact and lead models without modifying core modules, enabling:

- Duplicate contact detection via Facebook User ID
- Lead source tracking (Facebook, Instagram, etc.)
- Storage of original social media context

## Installation

```bash
# Via command line
./odoo-bin -u facebook_lead_integration -d your_database

# Or via Odoo UI: Apps → Update Apps List → Search "Facebook Lead" → Install
```

## Dependencies

- `crm` - Odoo CRM module
- `contacts` - Odoo Contacts module

## Module Structure

```
facebook_lead_integration/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── res_partner.py      # Contact model extension
│   └── crm_lead.py         # Lead model extension
└── views/
    ├── res_partner_views.xml
    └── crm_lead_views.xml
```

## Fields Reference

### res.partner (Contact)

| Technical Name | UI Label | Type | Notes |
|----------------|----------|------|-------|
| `x_facebook_id` | Facebook ID | Char | Indexed for fast lookup |
| `x_facebook_profile_url` | Facebook Profile | Char | URL widget in form |
| `x_lead_source` | Lead Source | Selection | See options below |
| `x_source_post_url` | Source Post URL | Char | URL widget in form |

### crm.lead (Lead/Opportunity)

| Technical Name | UI Label | Type | Notes |
|----------------|----------|------|-------|
| `x_facebook_comment_id` | Facebook Comment ID | Char | Original comment reference |
| `x_facebook_post_id` | Facebook Post ID | Char | Source post reference |
| `x_lead_source` | Lead Source | Selection | See options below |
| `x_source_url` | Source URL | Char | Comment/ad permalink |
| `x_original_message` | Original Message | Text | Full comment/message text |
| `x_post_context` | Post Context | Text | Context about source post |

### Lead Source Options

Both `x_lead_source` fields use identical selection options:

| Value | Label |
|-------|-------|
| `facebook_comment` | Facebook Comment |
| `facebook_ad` | Facebook Ad |
| `facebook_messenger` | Facebook Messenger |
| `instagram_comment` | Instagram Comment |
| `instagram_dm` | Instagram DM |
| `manual` | Manual Entry |
| `other` | Other |

## UI Additions

### Contact Views

1. **Form View:** New "Social Media" tab after "Internal Notes"
2. **List View:** Optional "Lead Source" column after email
3. **Search View:**
   - Search by Facebook ID
   - Filter: "Facebook Leads" (shows facebook_comment, facebook_ad, facebook_messenger sources)

### Lead Views

1. **Form View:** New "Social Media Source" tab after "Extra Info"
2. **List View:** "Lead Source" column after partner (visible by default)
3. **Search View:**
   - Filter: "Facebook Leads"
   - Filter: "Instagram Leads"
   - Group by: "Lead Source"

## API Usage

### Search Contact by Facebook ID

```python
# Python/Odoo
partner = self.env['res.partner'].search([
    ('x_facebook_id', '=', 'FACEBOOK_USER_ID')
], limit=1)
```

```json
// JSON-RPC
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      uid,
      "api_key",
      "res.partner",
      "search_read",
      [[["x_facebook_id", "=", "FACEBOOK_USER_ID"]]],
      {"fields": ["id", "name"], "limit": 1}
    ]
  }
}
```

### Create Contact with Facebook Data

```python
# Python/Odoo
partner = self.env['res.partner'].create({
    'name': 'John Doe',
    'x_facebook_id': 'FB_USER_ID',
    'x_facebook_profile_url': 'https://facebook.com/FB_USER_ID',
    'x_lead_source': 'facebook_comment',
    'x_source_post_url': 'https://facebook.com/page/posts/123'
})
```

### Create Lead with Facebook Context

```python
# Python/Odoo
lead = self.env['crm.lead'].create({
    'name': 'FB Lead: John Doe',
    'partner_id': partner.id,
    'x_lead_source': 'facebook_comment',
    'x_facebook_comment_id': 'COMMENT_ID',
    'x_facebook_post_id': 'POST_ID',
    'x_source_url': 'https://facebook.com/comment_permalink',
    'x_original_message': 'I am interested in your product!',
    'x_post_context': 'Post about new product launch...'
})
```

## Integration Points

This module is designed to work with:

1. **n8n Workflow** (`facebook-comments-to-odoo-leads.json`)
   - Receives Facebook webhooks
   - Creates contacts and leads via JSON-RPC

2. **Direct API Integration**
   - Any system can call Odoo's JSON-RPC/XML-RPC API
   - Use the field names documented above

## Extending This Module

### Adding New Source Types

Edit `models/res_partner.py` and `models/crm_lead.py`:

```python
x_lead_source = fields.Selection([
    ('facebook_comment', 'Facebook Comment'),
    # ... existing options ...
    ('tiktok', 'TikTok'),  # Add new option
    ('linkedin', 'LinkedIn'),
], string='Lead Source', default='manual')
```

### Adding Computed Fields

```python
# In crm_lead.py
x_is_social_lead = fields.Boolean(
    string='Is Social Media Lead',
    compute='_compute_is_social_lead',
    store=True
)

@api.depends('x_lead_source')
def _compute_is_social_lead(self):
    social_sources = ['facebook_comment', 'facebook_ad', 'instagram_comment']
    for lead in self:
        lead.x_is_social_lead = lead.x_lead_source in social_sources
```

## Related Documentation

- n8n Workflow: `/Users/kincheonglau/Claude Cowork/n8n/20260508-facebook/README.md`
- n8n Workflow JSON: `/Users/kincheonglau/Claude Cowork/n8n/20260508-facebook/facebook-comments-to-odoo-leads.json`
