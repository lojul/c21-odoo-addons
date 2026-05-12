# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SocialFeed(models.Model):
    _name = 'c21.social.feed'
    _description = 'RSS Feed Source'
    _order = 'priority, name'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='RSS URL', required=True)
    priority = fields.Integer(string='Priority', default=10, help='Lower number = higher priority')
    active = fields.Boolean(string='Active', default=True)
    language = fields.Selection([
        ('zh', 'Chinese'),
        ('en', 'English'),
    ], string='Language', default='zh')
    last_fetch = fields.Datetime(string='Last Fetch')
    news_count = fields.Integer(string='News Count', compute='_compute_news_count')

    @api.depends('name')
    def _compute_news_count(self):
        for feed in self:
            feed.news_count = self.env['c21.social.news'].search_count([
                ('feed_id', '=', feed.id)
            ])

    def action_fetch_now(self):
        """Manual fetch for this feed"""
        self.ensure_one()
        from ..utils import rss_scraper
        rss_scraper.fetch_feed(self.env, self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Fetched %s') % self.name,
                'type': 'success',
            }
        }

    @api.model
    def action_cleanup_news(self):
        """Cleanup old and invalid news"""
        news_model = self.env['c21.social.news']
        old_count = news_model.cleanup_old_news(days=7)
        invalid_count = news_model.cleanup_invalid_news()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Cleanup: %d old, %d invalid news removed') % (old_count, invalid_count),
                'type': 'success',
            }
        }
