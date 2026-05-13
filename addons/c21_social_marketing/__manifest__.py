# -*- coding: utf-8 -*-
{
    'name': 'C21 Social Marketing',
    'version': '19.0.1.2.0',
    'category': 'Marketing',
    'summary': 'Automated social media posts for Hong Kong property news',
    'description': """
C21 Social Marketing
====================
Automated social media posting for Century 21 Hong Kong.

Features:
- RSS news scraping from configurable sources
- AI-powered caption generation (DeepSeek via OpenRouter)
- Branded image generation with PIL
- Buffer API integration for FB/IG/Threads
- Approval workflow before posting
- Scheduled posting (configurable times)

Configuration:
- Settings → Social Marketing
- Add RSS feeds, API keys, channel IDs
    """,
    'author': 'C21 Net',
    'website': 'https://c21net.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/default_feeds.xml',
        'data/ir_cron.xml',
        'data/server_actions.xml',
        'views/social_post_views.xml',
        'views/social_channel_views.xml',
        'views/social_feed_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'c21_social_marketing/static/src/css/social_marketing.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
