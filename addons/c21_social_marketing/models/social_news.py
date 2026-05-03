# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SocialNews(models.Model):
    _name = 'c21.social.news'
    _description = 'Scraped News Item'
    _order = 'fetch_date desc, id desc'

    name = fields.Char(string='標題', required=True)
    description = fields.Text(string='描述')
    url = fields.Char(string='連結')
    source = fields.Char(string='來源')
    feed_id = fields.Many2one('c21.social.feed', string='RSS來源', ondelete='cascade')
    fetch_date = fields.Datetime(string='抓取時間', default=fields.Datetime.now)
    publish_date = fields.Datetime(string='發佈時間')
    used = fields.Boolean(string='已使用', default=False)
    post_ids = fields.Many2many('c21.social.post', string='相關帖文')

    # Property news relevance
    is_property_news = fields.Boolean(string='地產新聞', default=False)
    relevance_score = fields.Integer(string='相關性', default=0)

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
                    'message': '請先設定 OpenRouter API Key',
                    'type': 'danger',
                }
            }

        # Prepare news content
        news_content = f"標題: {self.name}\n來源: {self.source}\n摘要: {self.description[:500] if self.description else '無摘要'}"

        # Generate AI captions
        try:
            result = ai_generator.generate_captions(openrouter_key, news_content, model=ai_model)
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'AI 生成失敗: {str(e)}',
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
                    'message': f'圖片生成失敗: {str(e)}',
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
