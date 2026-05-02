{
    'name': 'C21 CSV Import',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Advanced CSV import with interactive column mapping for property listings',
    'description': """
C21 CSV Import
==============

Advanced CSV import module with:
- Multi-step wizard (Upload → Map → Preview → Import)
- Interactive column mapping with auto-detection
- Chinese district name conversion
- Price parsing (handles 萬, $, @, etc.)
- Date parsing (DD/MM/YYYY format)
- Preview with validation before import
- Persistent import logs
- Auto-generation of ref codes

Designed for importing property listings from SPP system.
    """,
    'author': 'C21',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['c21_property_listing'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/ir_sequence_data.xml',
        # Views
        'views/csv_import_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'c21_csv_import/static/src/css/csv_import.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
