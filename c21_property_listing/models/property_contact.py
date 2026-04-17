from odoo import models, fields


class C21PropertyContact(models.Model):
    _name = 'c21.property.contact'
    _description = 'Property Contact'
    _order = 'sequence, id'

    property_id = fields.Many2one(
        'c21.property.listing', string='Property',
        required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one(
        'res.partner', string='Name / 姓名',
        required=True, index=True)
    role = fields.Selection([
        ('landlord', 'Landlord'),
        ('property_manager', 'Property Manager'),
        ('building_manager', 'Building Manager'),
        ('leasing_agent', 'Leasing Agent'),
        ('legal', 'Legal Contact'),
        ('accounts', 'Accounts/Finance'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ], string='Title / 職稱', required=True, default='property_manager')
    is_primary = fields.Boolean('Primary Contact / 主要聯絡人', default=False)
    sequence = fields.Integer('Sequence', default=10)
    notes = fields.Text('Notes / 備註')

    # Writable related fields so edits here update the linked partner record.
    phone = fields.Char(related='partner_id.phone', string='Phone / 電話', readonly=False)
    email = fields.Char(related='partner_id.email', string='Email / 電郵', readonly=False)
