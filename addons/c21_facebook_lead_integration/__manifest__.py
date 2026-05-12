{
    'name': 'Facebook Lead Integration',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Capture leads from Facebook comments and ads',
    'description': """
        This module extends the CRM and Contacts modules to support
        Facebook lead capture via n8n workflow integration.

        Features:
        - Facebook ID field on contacts for duplicate detection
        - Lead source tracking fields
        - Facebook profile link storage
    """,
    'author': 'Custom',
    'depends': ['crm', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
