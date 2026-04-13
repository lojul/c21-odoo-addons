from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    c21_allowed_for_address = fields.Boolean(
        'C21 Allowed Country / C21 可用國家',
        default=False,
        help='If enabled, this country is available in C21 address country selections.')
