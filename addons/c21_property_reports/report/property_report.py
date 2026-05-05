# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import date


class PropertyParticularsReport(models.AbstractModel):
    """Report model for Property Particulars"""
    _name = 'report.c21_property_reports.report_property_particulars'
    _description = 'Property Particulars Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['c21.property.listing'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'c21.property.listing',
            'docs': docs,
            'data': data,
            'report_date': date.today().strftime('%Y-%m-%d'),
            'company': self.env.company,
        }


class PropertyComparisonReport(models.AbstractModel):
    """Report model for Property Comparison"""
    _name = 'report.c21_property_reports.report_property_comparison'
    _description = 'Property Comparison Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data and data.get('property_ids'):
            docs = self.env['c21.property.listing'].browse(data['property_ids'])
        else:
            docs = self.env['c21.property.listing'].browse(docids)

        # Calculate comparison metrics
        comparison_data = self._prepare_comparison_data(docs)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'c21.property.listing',
            'docs': docs,
            'data': data,
            'comparison': comparison_data,
            'report_date': date.today().strftime('%Y-%m-%d'),
            'company': self.env.company,
        }

    def _prepare_comparison_data(self, properties):
        """Prepare comparison metrics between properties"""
        if not properties:
            return {}

        # Calculate min/max/avg for key metrics
        areas = [p.gross_area for p in properties if p.gross_area]
        rents = [p.asking_rent for p in properties if p.asking_rent]
        prices_per_sqft = [p.rent_per_sqft for p in properties if p.rent_per_sqft]

        comparison = {
            'property_count': len(properties),
            'area': {
                'min': min(areas) if areas else 0,
                'max': max(areas) if areas else 0,
                'avg': sum(areas) / len(areas) if areas else 0,
            },
            'rent': {
                'min': min(rents) if rents else 0,
                'max': max(rents) if rents else 0,
                'avg': sum(rents) / len(rents) if rents else 0,
            },
            'price_per_sqft': {
                'min': min(prices_per_sqft) if prices_per_sqft else 0,
                'max': max(prices_per_sqft) if prices_per_sqft else 0,
                'avg': sum(prices_per_sqft) / len(prices_per_sqft) if prices_per_sqft else 0,
            },
        }

        # Identify best value (lowest price per sqft with valid data)
        valid_properties = [p for p in properties if p.rent_per_sqft and p.rent_per_sqft > 0]
        if valid_properties:
            best_value = min(valid_properties, key=lambda p: p.rent_per_sqft)
            comparison['best_value_id'] = best_value.id

        # Identify largest property
        valid_areas = [p for p in properties if p.gross_area and p.gross_area > 0]
        if valid_areas:
            largest = max(valid_areas, key=lambda p: p.gross_area)
            comparison['largest_id'] = largest.id

        return comparison
