# -*- coding: utf-8 -*-
{
    'name': 'C21 Property Reports',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'PDF reports for property listings - Particulars & Comparison',
    'description': """
C21 Property Reports
====================

Generate professional PDF reports for property listings:

* **Property Particulars** - Detailed single property report with images
* **Property Comparison** - Side-by-side comparison of multiple properties

Features:
- C21 Gold branding
- Cover images
- Key property details
- Amenities list
- Agent contact information
    """,
    'author': 'C21 Net',
    'website': 'https://c21net.com',
    'depends': [
        'c21_property_listing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/property_comparison_wizard_views.xml',
        'report/property_report.xml',
        'report/property_report_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'c21_property_reports/static/src/css/report.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
