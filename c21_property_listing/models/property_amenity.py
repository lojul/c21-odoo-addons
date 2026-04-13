from odoo import models, fields


class C21PropertyAmenity(models.Model):
    _name = 'c21.property.amenity'
    _description = 'Property Amenity'
    _order = 'category, name'

    name = fields.Char('Name (English) / 名稱（英文）', required=True, translate=True)
    name_cn = fields.Char('Name (Chinese) / 名稱（中文）')
    code = fields.Char('Code / 代碼', required=True, index=True)
    icon = fields.Char('Icon / 圖示', help='Icon class or name for UI display')
    category = fields.Selection([
        ('coworking', 'Co-working'),
        ('leasing', 'Leasing'),
        ('both', 'Both'),
    ], string='Category / 分類', default='both', required=True)
    active = fields.Boolean('Active / 啟用', default=True)

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Amenity code must be unique!',
    )
