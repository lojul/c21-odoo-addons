# n8n Workflows for Odoo-Website Integration

This folder contains n8n workflow definitions for automating property publishing from Odoo to the website.

## Workflows

### 1. `odoo-to-website-publish.json`

**Purpose:** Automatically publish properties from Odoo to the website when their status changes to "Ready to Publish".

**Flow:**
```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Schedule       │────>│  Config          │────>│  Odoo API        │────>│  Parse          │
│  (Every 5 min)  │     │  (credentials)   │     │  Search "ready"  │     │  Properties     │
└─────────────────┘     └──────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          v
                                               ┌──────────────────┐
                                               │  Is Coworking?   │
                                               └────────┬─────────┘
                                                   │         │
                                    ┌──────────────┘         └──────────────┐
                                    v                                        v
                         ┌─────────────────┐                     ┌─────────────────┐
                         │  Transform      │                     │  Transform      │
                         │  Coworking      │                     │  Leasing        │
                         └────────┬────────┘                     └────────┬────────┘
                                  │                                       │
                                  v                                       v
                         ┌─────────────────┐                     ┌─────────────────┐
                         │  POST to        │                     │  POST to        │
                         │  /api/listings  │                     │  /api/leasings  │
                         └────────┬────────┘                     └────────┬────────┘
                                  │                                       │
                                  v                                       v
                         ┌─────────────────┐                     ┌─────────────────┐
                         │  Update Odoo    │                     │  Update Odoo    │
                         │  → "published"  │                     │  → "published"  │
                         └─────────────────┘                     └─────────────────┘
```

## Setup Instructions

### Step 1: Import Workflow

1. Open your n8n instance: https://c21net.app.n8n.cloud
2. Click **Workflows** → **Add Workflow** → **Import from File**
3. Select `odoo-to-website-publish.json`

### Step 2: Configure Credentials

1. Open the imported workflow
2. Click on the **"Config"** node (yellow, at the start)
3. Edit the JSON to set your credentials:

```json
{
  "ODOO_URL": "https://188.166.189.244.nip.io",
  "ODOO_DB": "odoo",
  "ODOO_USER": "admin",
  "ODOO_API_KEY": "YOUR_API_KEY_HERE",
  "WEBSITE_URL": "https://coworkspace-main.vercel.app"
}
```

| Field | Description | Example |
|-------|-------------|---------|
| `ODOO_URL` | Odoo server URL | `https://188.166.189.244.nip.io` |
| `ODOO_DB` | Odoo database name | `odoo` |
| `ODOO_USER` | Odoo login username (not email!) | `admin` |
| `ODOO_API_KEY` | Odoo API key | `44e48be8...` |
| `WEBSITE_URL` | Website base URL | `https://coworkspace-main.vercel.app` |

### Step 3: Activate Workflow

1. Open the imported workflow
2. Click **Active** toggle in the top-right corner
3. The workflow will now run every 5 minutes

## How It Works

1. **Trigger**: Runs every 5 minutes (configurable)

2. **Fetch Ready Properties**: Queries Odoo for properties with `approval_status = 'ready'`

3. **Transform Data**:
   - Maps Odoo field names to website format
   - Converts district codes to Chinese names (e.g., `central` → `中環`)
   - Sets `status: 'approved'` for website
   - Adds `importedBy: 'odoo-n8n'` tracking field

4. **Route by Type**:
   - **Coworking** → POST to `/api/listings`
   - **Leasing** → POST to `/api/leasings`

5. **Update Odoo**: Changes `approval_status` from `ready` to `published`

## Field Mapping

### Coworking Properties (Odoo → Website)

| Odoo Field | Website Field |
|------------|---------------|
| `ref_code` | `refCode` |
| `name` | `name` |
| `name_cn` | `nameCn` |
| `district` | `district` (converted to Chinese) |
| `building_name` | `building` |
| `operator_id` | `operator` |
| `capacity` | `capacity` |
| `size` | `size` |
| `hot_desk_price` | `hotDeskPrice` |
| `dedicated_desk_price` | `dedicatedDeskPrice` |
| `office_price` | `officePrice` |

### Leasing Properties (Odoo → Website)

| Odoo Field | Website Field |
|------------|---------------|
| `ref_code` | `refCode` |
| `name` | `name` |
| `name_cn` | `nameCn` |
| `district` | `district` (converted to Chinese) |
| `property_type` | `propertyType` |
| `building_grade` | `buildingGrade` (A/B/C) |
| `gross_area` | `grossArea` |
| `net_area` | `netArea` |
| `asking_rent` | `monthlyRent` |
| `rent_per_sqft` | `pricePerSqft` |

## District Mapping

| Odoo Code | Chinese Name |
|-----------|--------------|
| `central` | 中環 |
| `admiralty` | 金鐘 |
| `wan_chai` | 灣仔 |
| `causeway_bay` | 銅鑼灣 |
| `tsim_sha_tsui` | 尖沙咀 |
| `mong_kok` | 旺角 |
| `kowloon_bay` | 九龍灣 |
| `kwun_tong` | 觀塘 |
| `tsuen_wan` | 荃灣 |
| ... | ... |

## Troubleshooting

### Workflow not triggering
- Check if the workflow is **Active** (toggle in top-right)
- Verify environment variables are set correctly
- Check n8n execution logs

### Authentication fails
- Verify `ODOO_USER` is the login username (e.g., `admin`), not email
- Regenerate API key if expired
- Test credentials with the API test script

### Properties not appearing on website
- Check website API is accessible
- Verify Cosmos DB credentials in Vercel
- Check n8n execution logs for errors

### Duplicate properties
- The workflow uses `id: odoo-{id}` format
- Website API may need upsert logic to prevent duplicates

## Manual Testing

1. In Odoo, create a property and set `approval_status` to "Ready to Publish"
2. In n8n, open the workflow and click **Execute Workflow**
3. Check the execution output for each node
4. Verify the property appears on the website
5. Verify Odoo status changed to "Published"

## Customization

### Change Schedule Interval
Edit the "Every 5 Minutes" node and adjust the interval.

### Add Error Notifications
Add an "If" node after POST to check for errors, then send email/Slack notification.

### Add Image Sync
Extend the transform nodes to fetch and map `image_ids` from Odoo.
