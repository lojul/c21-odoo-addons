from odoo import models, fields


class C21PropertyAmenity(models.Model):
    _name = 'c21.property.amenity'
    _description = 'Property Amenity'
    _order = 'category, name'

    name = fields.Char('Name (English)', required=True, translate=True)
    name_cn = fields.Char('Name (Chinese)')
    code = fields.Char('Code', required=True, index=True)
    icon = fields.Char('Icon', help='Icon class or name for UI display')
    category = fields.Selection([
        ('coworking', 'Co-working'),
        ('leasing', 'Leasing'),
        ('both', 'Both'),
    ], string='Category', default='both', required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Amenity code must be unique!'),
    ]
