{
    'name': 'C21 Admin Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Administration',
    'summary': 'Admin dashboard for tracking modules and changes',
    'description': """
C21 Admin Dashboard
===================

A centralized admin dashboard for system administrators to:
- View all installed modules
- Track custom C21 modules
- Maintain a changelog of system changes
- Quick access to common admin functions

This module is standalone and can be installed independently.
    """,
    'author': 'C21',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Views
        'views/admin_dashboard_views.xml',
        'views/menu.xml',
        # Data
        'data/changelog_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
