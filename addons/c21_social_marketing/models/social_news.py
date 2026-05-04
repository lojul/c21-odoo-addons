# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SocialNews(models.Model):
    _name = 'c21.social.news'
    _description = 'Scraped News Item'
    _order = 'fetch_date desc, id desc'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    url = fields.Char(string='URL')
    source = fields.Char(string='Source')
    feed_id = fields.Many2one('c21.social.feed', string='RSS Feed', ondelete='cascade')
    fetch_date = fields.Datetime(string='Fetch Date', default=fields.Datetime.now)
    publish_date = fields.Datetime(string='Publish Date')
    used = fields.Boolean(string='Used', default=False)
    post_ids = fields.Many2many('c21.social.post', string='Related Posts')

    # Property news relevance
    is_property_news = fields.Boolean(string='Property News', default=False)
    relevance_score = fields.Integer(string='Relevance Score', default=0)

    # URL uniqueness handled in code (search before create)

    @api.model
    def cleanup_old_news(self, days=30):
        """Remove news older than X days"""
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        old_news = self.search([
            ('fetch_date', '<', cutoff),
            ('used', '=', False)
        ])
        old_news.unlink()
        return len(old_news)

    def action_create_post(self):
        """Create a social post from this news item"""
        self.ensure_one()

        # Import utilities
        from ..utils import ai_generator, image_generator

        ICP = self.env['ir.config_parameter'].sudo()
        openrouter_key = ICP.get_param('c21_social_marketing.openrouter_api_key')
        ai_model = ICP.get_param('c21_social_marketing.ai_model', 'deepseek/deepseek-chat')

        if not openrouter_key:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Please configure OpenRouter API Key first'),
                    'type': 'danger',
                }
            }

        # Prepare news content
        news_content = f"Title: {self.name}\nSource: {self.source}\nSummary: {self.description[:500] if self.description else 'No summary'}"

        # Generate AI captions
        try:
            result = ai_generator.generate_captions(openrouter_key, news_content, model=ai_model)
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('AI generation failed: %s') % str(e),
                    'type': 'danger',
                }
            }

        # Generate image
        try:
            headline = result.get('headline_zh', self.name[:20])
            data_point = result.get('data_point', '')
            background = result.get('background_color', 'navy_blue')
            image_base64 = image_generator.generate_post_image(headline, data_point, background)
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Image generation failed: %s') % str(e),
                    'type': 'danger',
                }
            }

        # Get all active channels
        channels = self.env['c21.social.channel'].search([('active', '=', True)])

        # Create post
        post = self.env['c21.social.post'].create({
            'headline_zh': result.get('headline_zh', self.name[:50]),
            'data_point': result.get('data_point', ''),
            'district': result.get('district', ''),
            'source': self.source,
            'news_ids': [(6, 0, [self.id])],
            'channel_ids': [(6, 0, channels.ids)],
            'ig_caption': result.get('ig_caption', ''),
            'fb_caption': result.get('fb_caption', ''),
            'threads_caption': result.get('threads_caption', ''),
            'image': image_base64,
            'background_color': background,
            'state': 'pending',
        })

        # Mark news as used
        self.used = True

        # Open the created post
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c21.social.post',
            'res_id': post.id,
            'view_mode': 'form',
            'target': 'current',
        }
