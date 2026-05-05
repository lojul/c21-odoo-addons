# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PropertyComparisonWizard(models.TransientModel):
    """Wizard to select properties for comparison report"""
    _name = 'c21.property.comparison.wizard'
    _description = 'Property Comparison Wizard'

    property_ids = fields.Many2many(
        'c21.property.listing',
        string='Properties to Compare',
        required=True,
        help='Select 2-5 properties to compare'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Pre-fill with selected properties from context
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['property_ids'] = [(6, 0, active_ids)]
        return res

    def action_generate_report(self):
        """Generate the comparison report"""
        self.ensure_one()

        if len(self.property_ids) < 2:
            raise UserError(_('Please select at least 2 properties to compare.'))

        if len(self.property_ids) > 5:
            raise UserError(_('Please select no more than 5 properties to compare.'))

        # Return report action with property IDs
        return self.env.ref('c21_property_reports.action_report_property_comparison').report_action(
            self.property_ids,
            data={'property_ids': self.property_ids.ids}
        )
