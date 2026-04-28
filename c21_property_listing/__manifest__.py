{
    'name': 'C21 Property Management',
    'version': '19.0.3.0.0',
    'category': 'Real Estate',
    'summary': 'Manage co-working spaces and leasing properties',
    'description': """
C21 Property Management
=======================

Unified property management for:
- Co-working spaces (hot desk, dedicated desk, private office)
- Leasing properties (office, retail, industrial)

Features:
- Bilingual support (English/Chinese)
- Image storage with automatic resizing (small/medium/large)
- Auto-download images from URLs
- Amenities tracking
- Approval workflow
- Mass update actions
- REST API for website integration

v19.0.3.0.0 - Added:
- Sale pricing fields (售價, 底售, 售呎價, 底售呎價)
- Floor rental fields (底租, 底租呎價)
- Yield rate calculation (回報率)
- Room layout (間隔)
- Tenant info (租客)
- Key holder (鎖匙)
- Source tracking (來源)
- Follow-up date (跟進日期)
- Listing date (開盤日期)
- DD Lot reference
- Responsible person (負責同事)

This module is standalone with no dependencies on CRM or other custom modules.
    """,
    'author': 'C21',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/property_amenity_data.xml',
        'data/country_whitelist_data.xml',
        'data/server_actions.xml',
        # Views
        'views/property_listing_views.xml',
        'views/property_image_views.xml',
        'views/property_operator_views.xml',
        'views/res_country_views.xml',
        'views/property_amenity_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'c21_property_listing/static/src/css/operator_list.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
