import base64
import csv
import io
import json
import re
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


# District mapping: Chinese → code
DISTRICT_CN_MAP = {
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
    # Additional mappings for SPP data
    '炮台山': 'north_point',
    '天后': 'causeway_bay',
    '藍田': 'kwun_tong',
    '匡湖居': 'other',
    '柴灣': 'other',
    '西貢': 'other',
    '將軍澳': 'po_lam',
    '紅磡': 'whampoa',
    '土瓜灣': 'jordan',
    '何文田': 'jordan',
    '油麻地': 'jordan',
    '大角咀': 'mong_kok',
    '奧運': 'mong_kok',
    '石硤尾': 'sham_shui_po',
    '荔枝角': 'cheung_sha_wan',
    '美孚': 'cheung_sha_wan',
    '油塘': 'kwun_tong',
    '牛頭角': 'kwun_tong',
    '九龍城': 'kowloon_bay',
    '鑽石山': 'san_po_kong',
    '彩虹': 'san_po_kong',
    '大圍': 'sha_tin',
    '馬鞍山': 'sha_tin',
    '粉嶺': 'tai_po',
    '上水': 'tai_po',
    '天水圍': 'yuen_long',
    '東涌': 'other',
    '青衣': 'tsuen_wan',
    '離島': 'other',
}

# Auto-mapping rules: lowercase CSV header → Odoo field
# Supports both English and Chinese column names, and bilingual formats like "English / 中文"
AUTO_MAP = {
    # Name fields
    'english name': 'name',
    'english name / 英文名稱': 'name',
    '英文名稱': 'name',
    'chinese name': 'name_cn',
    'chinese name / 中文名稱': 'name_cn',
    '中文名稱': 'name_cn',
    # Ref code
    'ref code': 'ref_code',
    'ref code / 編號': 'ref_code',
    '編號': 'ref_code',
    # Type
    'type': 'listing_type',
    'type / 類型': 'listing_type',
    '類型': 'listing_type',
    # District
    'district': 'district',
    'district / 地區': 'district',
    '地區': 'district',
    # Address fields
    'street': 'address',
    'street / 街道': 'address',
    '街道': 'address',
    'building': 'building_name',
    'building / 物業名稱': 'building_name',
    '物業名稱': 'building_name',
    'floor': 'floor',
    'floor / 樓層': 'floor',
    '樓層': 'floor',
    'unit': 'unit',
    'unit / 室號': 'unit',
    '室號': 'unit',
    # Property type
    'prop type': 'property_type_id',
    'prop type / 用途': 'property_type_id',
    '用途': 'property_type_id',
    # Area fields
    'gross sqft': 'gross_area',
    'gross sqft / 建呎': 'gross_area',
    '建呎': 'gross_area',
    'total area': 'total_area',
    'total area / 總面積': 'total_area',
    '總面積': 'total_area',
    # Rent fields
    'rent': 'asking_rent',
    'rent / 租價': 'asking_rent',
    '租價': 'asking_rent',
    'floor rent': 'floor_rent',
    'floor rent / 底租': 'floor_rent',
    '底租': 'floor_rent',
    # Sale fields
    'sale price': 'selling_price',
    'sale price / 售價(萬)': 'selling_price',
    '售價': 'selling_price',
    '售價(萬)': 'selling_price',
    'floor sale': 'floor_selling_price',
    'floor sale / 底售(萬)': 'floor_selling_price',
    '底售': 'floor_selling_price',
    '底售(萬)': 'floor_selling_price',
    # Other fields
    'year built': 'year_built',
    'year built / 樓齡': 'year_built',
    '樓齡': 'year_built',
    'layout': 'room_layout',
    'layout / 間隔': 'room_layout',
    '間隔': 'room_layout',
    'internal notes': 'internal_notes',
    'internal notes / 提示': 'internal_notes',
    '提示': 'internal_notes',
    'description': 'description',
    'description / 描述': 'description',
    '描述': 'description',
    'follow-up': 'followup_date',
    'follow-up / 跟進日期': 'followup_date',
    '跟進日期': 'followup_date',
    'publish': 'approval_status',
    'publish / 發佈': 'approval_status',
    '發佈': 'approval_status',
    'source': 'source_id',
    'source / 來源': 'source_id',
    '來源': 'source_id',
}


def parse_price(value, is_wan=False):
    """Parse price strings like '$16.4萬', '$69,000', '@109.33'."""
    if not value:
        return 0.0

    value = str(value).strip()
    if not value:
        return 0.0

    # Remove common prefixes/suffixes
    value = value.replace('$', '').replace('@', '').replace(',', '').strip()

    # Handle 萬 (10,000) multiplier
    if '萬' in value:
        value = value.replace('萬', '')
        multiplier = 10000
    elif is_wan:
        multiplier = 10000
    else:
        multiplier = 1

    try:
        return float(value) * multiplier
    except ValueError:
        return 0.0


def parse_date(value):
    """Parse DD/MM/YYYY format."""
    if not value:
        return False
    try:
        return datetime.strptime(value.strip(), '%d/%m/%Y').date()
    except ValueError:
        try:
            # Try YYYY-MM-DD format
            return datetime.strptime(value.strip(), '%Y-%m-%d').date()
        except ValueError:
            return False


def parse_district(value):
    """Convert Chinese district name to selection code."""
    if not value:
        return False

    value = str(value).strip()

    # Direct match in mapping
    if value in DISTRICT_CN_MAP:
        return DISTRICT_CN_MAP[value]

    # Check if it's already a valid code
    valid_codes = [
        'central', 'admiralty', 'wan_chai', 'causeway_bay', 'north_point',
        'quarry_bay', 'taikoo', 'wong_chuk_hang', 'sheung_wan', 'sai_ying_pun',
        'tsim_sha_tsui', 'jordan', 'mong_kok', 'kowloon_bay', 'kwun_tong',
        'san_po_kong', 'cheung_sha_wan', 'sham_shui_po', 'whampoa',
        'kwai_chung', 'tsuen_wan', 'sha_tin', 'fo_tan', 'tuen_mun',
        'yuen_long', 'po_lam', 'tai_po', 'other'
    ]
    if value.lower().replace(' ', '_') in valid_codes:
        return value.lower().replace(' ', '_')

    return 'other'


class CsvImportWizard(models.TransientModel):
    _name = 'c21.csv.import.wizard'
    _description = 'CSV Import Wizard'

    state = fields.Selection([
        ('upload', 'Upload'),
        ('mapping', 'Mapping'),
        ('preview', 'Preview'),
        ('done', 'Done'),
    ], default='upload', string='State')

    # File upload
    csv_file = fields.Binary('CSV File')
    csv_filename = fields.Char('Filename')
    delimiter = fields.Selection([
        (',', 'Comma (,)'),
        (';', 'Semicolon (;)'),
        ('\t', 'Tab'),
    ], default=',', string='Delimiter')
    skip_header = fields.Boolean('First Row is Header', default=True)

    # Column mappings
    mapping_ids = fields.One2many(
        'c21.csv.import.line', 'wizard_id', string='Column Mappings')

    # Preview data (stored as JSON)
    preview_data = fields.Text('Preview JSON')
    preview_html = fields.Html('Preview', compute='_compute_preview_html', sanitize=False)

    # Results
    total_rows = fields.Integer('Total Rows')
    success_count = fields.Integer('Imported')
    error_count = fields.Integer('Errors')
    error_details = fields.Text('Error Details')
    log_id = fields.Many2one('c21.csv.import.log', 'Import Log')

    @api.depends('preview_data')
    def _compute_preview_html(self):
        for record in self:
            if not record.preview_data:
                record.preview_html = ''
                continue

            try:
                data = json.loads(record.preview_data)
                rows = data.get('rows', [])
                headers = data.get('headers', [])
                errors = data.get('errors', [])

                html = ['<table class="table table-sm table-bordered csv-preview-table">']

                # Header row
                html.append('<thead><tr>')
                for h in headers:
                    html.append(f'<th>{h}</th>')
                html.append('</tr></thead>')

                # Data rows
                html.append('<tbody>')
                for i, row in enumerate(rows[:10]):  # First 10 rows
                    row_errors = [e for e in errors if e.get('row') == i]
                    row_class = 'table-danger' if row_errors else ''
                    html.append(f'<tr class="{row_class}">')
                    for cell in row:
                        html.append(f'<td>{cell if cell else ""}</td>')
                    html.append('</tr>')
                html.append('</tbody>')

                html.append('</table>')

                if len(rows) > 10:
                    html.append(f'<p class="text-muted">... and {len(rows) - 10} more rows</p>')

                record.preview_html = ''.join(html)
            except (json.JSONDecodeError, KeyError):
                record.preview_html = '<p class="text-danger">Error loading preview</p>'

    def _read_csv_file(self):
        """Read and parse the CSV file."""
        if not self.csv_file:
            raise UserError(_('Please upload a CSV file.'))

        try:
            content = base64.b64decode(self.csv_file).decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                content = base64.b64decode(self.csv_file).decode('gbk')
            except UnicodeDecodeError:
                content = base64.b64decode(self.csv_file).decode('latin-1')

        reader = csv.reader(io.StringIO(content), delimiter=self.delimiter)
        rows = list(reader)

        if not rows:
            raise UserError(_('The CSV file is empty.'))

        return rows

    def _auto_map_column(self, header):
        """Try to auto-map a CSV column to an Odoo field."""
        header_lower = header.lower().strip()

        # Direct match
        if header_lower in AUTO_MAP:
            return AUTO_MAP[header_lower]

        # Partial match
        for key, field in AUTO_MAP.items():
            if key in header_lower or header_lower in key:
                return field

        return 'skip'

    def action_parse(self):
        """Parse the CSV file and create column mappings."""
        self.ensure_one()
        rows = self._read_csv_file()

        # Get headers and sample data
        if self.skip_header:
            headers = rows[0] if rows else []
            sample_row = rows[1] if len(rows) > 1 else [''] * len(headers)
        else:
            headers = [f'Column {i+1}' for i in range(len(rows[0]))]
            sample_row = rows[0] if rows else []

        # Clear existing mappings
        self.mapping_ids.unlink()

        # Create mapping lines
        mapping_vals = []
        for i, header in enumerate(headers):
            sample = sample_row[i] if i < len(sample_row) else ''
            odoo_field = self._auto_map_column(header)

            mapping_vals.append({
                'wizard_id': self.id,
                'sequence': i,
                'csv_column': header,
                'sample_data': str(sample)[:100],  # Truncate long samples
                'odoo_field': odoo_field,
            })

        self.env['c21.csv.import.line'].create(mapping_vals)

        self.total_rows = len(rows) - (1 if self.skip_header else 0)
        self.state = 'mapping'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c21.csv.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_field_mapping(self):
        """Get mapping of column index to Odoo field."""
        mapping = {}
        for line in self.mapping_ids:
            if line.odoo_field != 'skip':
                mapping[line.sequence] = line.odoo_field
        return mapping

    def _transform_row(self, row, mapping):
        """Transform a CSV row to Odoo field values."""
        vals = {}
        errors = []

        for col_idx, field_name in mapping.items():
            if col_idx >= len(row):
                continue

            value = row[col_idx].strip() if row[col_idx] else ''

            if field_name == 'district':
                vals['district'] = parse_district(value)
                if not vals['district']:
                    vals['district'] = 'other'

            elif field_name in ('asking_rent', 'floor_rent'):
                vals[field_name] = parse_price(value)

            elif field_name in ('selling_price', 'floor_selling_price'):
                # These are stored in 萬, so check if value contains 萬
                if '萬' in value:
                    vals[field_name] = parse_price(value) / 10000
                else:
                    vals[field_name] = parse_price(value, is_wan=True) / 10000

            elif field_name in ('gross_area', 'net_area', 'total_area'):
                try:
                    cleaned = re.sub(r'[^\d.]', '', value)
                    vals[field_name] = float(cleaned) if cleaned else 0.0
                except ValueError:
                    vals[field_name] = 0.0

            elif field_name == 'followup_date':
                date_val = parse_date(value)
                if date_val:
                    vals['followup_date'] = date_val

            elif field_name == 'property_type_id':
                vals['_property_type_name'] = value

            elif field_name == 'source_id':
                vals['_source_name'] = value

            elif field_name == 'room_layout':
                # Try to map layout values
                layout_map = {
                    'studio': 'studio',
                    '開放式': 'studio',
                    '1房': '1br',
                    '1br': '1br',
                    '2房': '2br',
                    '2br': '2br',
                    '3房': '3br',
                    '3br': '3br',
                    '4房': '4br_plus',
                    '4+': '4br_plus',
                }
                vals['room_layout'] = layout_map.get(value.lower(), False)

            elif field_name == 'approval_status':
                status_map = {
                    'draft': 'draft',
                    '草稿': 'draft',
                    'ready': 'ready',
                    '待發佈': 'ready',
                    'published': 'published',
                    '已發佈': 'published',
                }
                vals['approval_status'] = status_map.get(value.lower(), 'draft')

            elif field_name == 'listing_type':
                type_map = {
                    'coworking': 'coworking',
                    'coworking space': 'coworking',
                    'co-working space': 'coworking',
                    'co-working': 'coworking',
                    '共享': 'coworking',
                    '共享空間': 'coworking',
                    'leasing': 'leasing',
                    'leasing property': 'leasing',
                    '租賃': 'leasing',
                    '出租': 'leasing',
                }
                vals['listing_type'] = type_map.get(value.lower(), 'leasing')

            else:
                vals[field_name] = value

        return vals, errors

    def _resolve_relations(self, vals):
        """Resolve relational fields like property_type_id and source_id."""
        # Property Type
        if '_property_type_name' in vals:
            type_name = vals.pop('_property_type_name')
            if type_name:
                PropertyType = self.env['c21.property.type']
                prop_type = PropertyType.search([
                    '|', ('name', 'ilike', type_name),
                    ('name_cn', 'ilike', type_name)
                ], limit=1)
                if prop_type:
                    vals['property_type_id'] = prop_type.id

        # Source
        if '_source_name' in vals:
            source_name = vals.pop('_source_name')
            if source_name:
                Source = self.env['c21.property.source']
                source = Source.search([
                    '|', ('name', 'ilike', source_name),
                    ('code', 'ilike', source_name)
                ], limit=1)
                if not source:
                    # Create new source
                    source = Source.create({
                        'name': source_name,
                        'name_cn': source_name,
                        'code': source_name.lower().replace(' ', '_'),
                    })
                vals['source_id'] = source.id

        return vals

    def action_preview(self):
        """Generate preview of the import."""
        self.ensure_one()
        rows = self._read_csv_file()
        mapping = self._get_field_mapping()

        if self.skip_header:
            data_rows = rows[1:]
        else:
            data_rows = rows

        # Get mapped field names for headers
        headers = []
        for line in self.mapping_ids.sorted('sequence'):
            if line.odoo_field != 'skip':
                headers.append(line.csv_column)

        preview_rows = []
        errors = []
        valid_count = 0

        for i, row in enumerate(data_rows):
            transformed, row_errors = self._transform_row(row, mapping)

            # Validate required fields
            if not transformed.get('name') and not transformed.get('name_cn'):
                row_errors.append({'row': i, 'msg': 'Missing name'})

            if not transformed.get('district'):
                row_errors.append({'row': i, 'msg': 'Missing district'})

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_count += 1

            # Build preview row (only mapped columns)
            preview_row = []
            for line in self.mapping_ids.sorted('sequence'):
                if line.odoo_field != 'skip':
                    col_idx = line.sequence
                    val = row[col_idx] if col_idx < len(row) else ''
                    preview_row.append(val)

            preview_rows.append(preview_row)

        self.preview_data = json.dumps({
            'headers': headers,
            'rows': preview_rows,
            'errors': errors,
        })

        self.error_count = len(set(e['row'] for e in errors))
        self.total_rows = len(data_rows)
        self.state = 'preview'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c21.csv.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import(self):
        """Import the CSV data into property listings."""
        self.ensure_one()
        rows = self._read_csv_file()
        mapping = self._get_field_mapping()

        if self.skip_header:
            data_rows = rows[1:]
        else:
            data_rows = rows

        PropertyListing = self.env['c21.property.listing']
        created_ids = []
        error_details = []

        for i, row in enumerate(data_rows):
            try:
                vals, _ = self._transform_row(row, mapping)
                vals = self._resolve_relations(vals)

                # Set defaults
                if 'listing_type' not in vals:
                    vals['listing_type'] = 'leasing'

                # Generate ref_code if not provided
                if not vals.get('ref_code'):
                    vals['ref_code'] = self.env['ir.sequence'].next_by_code(
                        'c21.property.listing.ref_code'
                    ) or f'CSV-{i+1}'

                # Set name from name_cn if not provided
                if not vals.get('name') and vals.get('name_cn'):
                    vals['name'] = vals['name_cn']
                elif not vals.get('name'):
                    vals['name'] = vals.get('ref_code', f'Property {i+1}')

                # Set district default
                if not vals.get('district'):
                    vals['district'] = 'other'

                # Auto-fill total_area from gross_area
                if vals.get('gross_area') and not vals.get('total_area'):
                    vals['total_area'] = vals['gross_area']

                # Create the property
                prop = PropertyListing.create(vals)
                created_ids.append(prop.id)

            except Exception as e:
                error_details.append(f"Row {i+1}: {str(e)}")

        # Create import log
        log = self.env['c21.csv.import.log'].create({
            'name': self.csv_filename or 'Unknown',
            'status': 'completed' if not error_details else 'partial',
            'total_rows': len(data_rows),
            'success_count': len(created_ids),
            'error_count': len(error_details),
            'property_ids': [(6, 0, created_ids)],
            'error_details': '\n'.join(error_details) if error_details else False,
        })

        self.success_count = len(created_ids)
        self.error_count = len(error_details)
        self.error_details = '\n'.join(error_details) if error_details else False
        self.log_id = log.id
        self.state = 'done'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c21.csv.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_log(self):
        """Open the import log."""
        self.ensure_one()
        if not self.log_id:
            raise UserError(_('No import log found.'))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c21.csv.import.log',
            'res_id': self.log_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_properties(self):
        """Open the created properties."""
        self.ensure_one()
        if not self.log_id or not self.log_id.property_ids:
            raise UserError(_('No properties were created.'))

        return self.log_id.action_view_properties()
