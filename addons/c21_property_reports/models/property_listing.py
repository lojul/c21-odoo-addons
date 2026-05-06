# -*- coding: utf-8 -*-
from odoo import models


class PropertyListingReport(models.Model):
    _inherit = 'c21.property.listing'

    def action_print_particulars(self):
        """Print the Property Particulars PDF report"""
        self.ensure_one()
        return self.env.ref('c21_property_reports.action_report_property_particulars').report_action(self)
