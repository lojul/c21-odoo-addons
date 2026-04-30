{
    'name': 'C21 PDF Import',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Import property listings from PDF via n8n workflow',
    'description': """
C21 PDF Import
==============

Trigger n8n workflow to process PDF files from OneDrive:
- Extract property data using AI (Azure OCR + Llama)
- Create/update Odoo listings automatically
- Index to vector database for AI chatbot search
- View import history and status
    """,
    'author': 'Century 21',
    'depends': ['base', 'c21_property_listing'],
    'data': [
        'security/ir.model.access.csv',
        'views/pdf_import_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
