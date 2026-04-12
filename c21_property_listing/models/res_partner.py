from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    @api.onchange('is_property_operator')
    def _onchange_is_property_operator(self):
        # Operator records must be companies so they can own child contact persons.
        if self.is_property_operator:
            self.is_company = True
            if 'company_type' in self._fields:
                self.company_type = 'company'

    @api.constrains('is_property_operator', 'is_company')
    def _check_operator_is_company(self):
        for partner in self:
            if partner.is_property_operator and not partner.is_company:
                raise ValidationError('Property Operator must be a company.')
