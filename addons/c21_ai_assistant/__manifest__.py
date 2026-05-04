# -*- coding: utf-8 -*-
{
    'name': 'C21 - AI Assistant',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'AI-powered assistant for property and CRM search',
    'description': """
C21 AI Assistant
================

An intelligent assistant that helps users:
- Search property listings using natural language
- Query CRM leads and contacts
- Search property documents via RAG (n8n integration)
- Answer general questions

Features:
- Configurable LLM providers (OpenRouter, Azure OpenAI, Ollama)
- Customizable system prompts
- Feature toggles for different search capabilities
- Chat history and session management
- Access control via user groups
    """,
    'author': 'C21Net',
    'website': 'https://c21net.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/ai_assistant_security.xml',
        'security/ir.model.access.csv',
        'data/ai_config_data.xml',
        'views/res_config_settings_views.xml',
        'views/ai_chat_session_views.xml',
        'views/ai_assistant_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'c21_ai_assistant/static/src/css/ai_chat.css',
            'c21_ai_assistant/static/src/js/ai_chat_service.js',
            'c21_ai_assistant/static/src/js/ai_chat_widget.js',
            'c21_ai_assistant/static/src/xml/ai_chat_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
