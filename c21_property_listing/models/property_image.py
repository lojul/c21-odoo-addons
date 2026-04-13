from odoo import models, fields


class C21PropertyImage(models.Model):
    _name = 'c21.property.image'
    _description = 'Property Image'
    _order = 'sequence, id'

    property_id = fields.Many2one(
        'c21.property.listing', string='Property',
        required=True, ondelete='cascade', index=True)
    name = fields.Char('Description / 描述', help='Image description or alt text')
    image_url = fields.Char('Image URL / 圖片網址', required=True, help='Full URL to the image on CDN')
    thumbnail_url = fields.Char('Thumbnail URL / 縮圖網址', help='URL to thumbnail version')
    sequence = fields.Integer('Sequence / 排序', default=10)
    is_cover = fields.Boolean('Is Cover Image / 是否封面圖', default=False)
