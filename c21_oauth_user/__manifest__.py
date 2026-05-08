{
    'name': 'C21 OAuth User Management',
    'version': '19.0.1.9.0',
    'category': 'Tools',
    'summary': 'SSO user management - OAuth fields, auto-confirm, no invitation emails',
    'description': """
        This module:
        - Adds OAuth Provider and OAuth UID fields to the user form for easy SSO setup
        - Auto-confirms SSO users (no invitation email needed)
        - Skips password reset emails for SSO users
        - Automatically cleans up orphaned partner records when users are deleted
    """,
    'author': 'Century 21',
    'depends': ['base', 'auth_oauth', 'auth_signup'],
    'data': [
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
