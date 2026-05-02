from odoo import models, fields


class CsvImportLine(models.TransientModel):
    _name = 'c21.csv.import.line'
    _description = 'CSV Import Column Mapping'
    _order = 'sequence'

    wizard_id = fields.Many2one(
        'c21.csv.import.wizard', string='Wizard',
        ondelete='cascade', required=True)
    sequence = fields.Integer('Column Index')
    csv_column = fields.Char('CSV Column')
    sample_data = fields.Char('Sample Value')

    odoo_field = fields.Selection([
        ('skip', '-- Skip --'),
        ('name', 'Name (EN)'),
        ('name_cn', 'Name (CN)'),
        ('ref_code', 'Ref Code'),
        ('listing_type', 'Listing Type'),
        ('district', 'District'),
        ('address', 'Street Address'),
        ('building_name', 'Building Name'),
        ('floor', 'Floor'),
        ('unit', 'Unit'),
        ('property_type_id', 'Property Type'),
        ('source_id', 'Source'),
        ('gross_area', 'Gross Area (sqft)'),
        ('total_area', 'Total Area'),
        ('net_area', 'Net Area'),
        ('asking_rent', 'Asking Rent'),
        ('floor_rent', 'Floor Rent'),
        ('selling_price', 'Sale Price'),
        ('floor_selling_price', 'Floor Sale'),
        ('year_built', 'Year Built'),
        ('room_layout', 'Layout'),
        ('internal_notes', 'Internal Notes'),
        ('description', 'Description'),
        ('followup_date', 'Follow-up Date'),
        ('approval_status', 'Publish Status'),
    ], default='skip', string='Map To', required=True)
