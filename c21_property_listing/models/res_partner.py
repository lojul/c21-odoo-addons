from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_property_operator = fields.Boolean(
        'Is Property Operator', default=False,
        help='Check if this partner is a co-working space operator')
    operator_logo_url = fields.Char(
        'Operator Logo URL',
        help='External URL to operator logo image')
    property_ids = fields.One2many(
        'c21.property.listing', 'operator_id',
        string='Properties')
    property_count = fields.Integer(
        'Property Count', compute='_compute_property_count')

    @api.depends('property_ids')
    def _compute_property_count(self):
        for partner in self:
            partner.property_count = len(partner.property_ids)
