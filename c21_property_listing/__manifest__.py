{
    'name': 'C21 Property Listing',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Manage co-working spaces and leasing properties',
    'description': """
C21 Property Listing
====================

Unified property management for:
- Co-working spaces (hot desk, dedicated desk, private office)
- Leasing properties (office, retail, industrial)

Features:
- Bilingual support (English/Chinese)
- Multi-image management (external CDN URLs)
- Amenities tracking
- Approval workflow
- REST API for website integration (Phase 3)

This module is standalone with no dependencies on CRM or other custom modules.
    """,
    'author': 'C21',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/property_amenity_data.xml',
        # Views
        'views/property_listing_views.xml',
        'views/property_operator_views.xml',
        'views/property_amenity_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
