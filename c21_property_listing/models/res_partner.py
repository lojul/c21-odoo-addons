from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_property_operator = fields.Boolean(
        'Is Property Operator / 是否物業營運商', default=False,
        help='Check if this partner is a co-working space operator')
    operator_logo_url = fields.Char(
        'Operator Logo URL / 營運商標誌網址',
        help='External URL to operator logo image')
    property_ids = fields.One2many(
        'c21.property.listing', 'operator_id',
        string='Properties / 物業')
    property_count = fields.Integer(
        'Property Count / 物業數量', compute='_compute_property_count')
    operator_contact_person = fields.Char(
        'Contact Person / 聯絡人', compute='_compute_operator_contact_person')
    operator_contact_partner_id = fields.Many2one(
        'res.partner', string='Contact Record / 聯絡記錄', compute='_compute_operator_contact_person')

    @api.depends('property_ids')
    def _compute_property_count(self):
        for partner in self:
            partner.property_count = len(partner.property_ids)

    @api.depends('child_ids.name', 'child_ids.is_company', 'child_ids.type')
    def _compute_operator_contact_person(self):
        for partner in self:
            contacts = partner.child_ids.filtered(lambda c: (c.type == 'contact') or (not c.is_company))
            first = contacts[:1]
            partner.operator_contact_person = first.name if first else False
            partner.operator_contact_partner_id = first.id if first else False

    def action_open_operator_properties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Properties',
            'res_model': 'c21.property.listing',
            'view_mode': 'list,kanban,form',
            'domain': [('operator_id', '=', self.id)],
            'context': {'default_operator_id': self.id},
        }

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
