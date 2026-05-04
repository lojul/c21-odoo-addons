# -*- coding: utf-8 -*-
import logging
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SocialPost(models.Model):
    _name = 'c21.social.post'
    _description = 'Social Media Post'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)

    # Content
    headline_zh = fields.Char(string='Chinese Headline', required=True, tracking=True)
    data_point = fields.Char(string='Data Point', tracking=True)
    district = fields.Char(string='District')
    source = fields.Char(string='News Source')

    # Captions per platform
    ig_caption = fields.Text(string='Instagram Caption')
    fb_caption = fields.Text(string='Facebook Caption')
    threads_caption = fields.Text(string='Threads Caption')

    # Image
    background_color = fields.Selection([
        ('navy_blue', 'Navy Blue (Default)'),
        ('sage_green', 'Sage Green (Positive)'),
        ('charcoal', 'Charcoal (Cautious)'),
        ('terracotta', 'Terracotta (Major Deal)'),
    ], string='Background Color', default='navy_blue', tracking=True)
    image = fields.Binary(string='Image', attachment=True)
    image_filename = fields.Char(string='Image Filename')
    image_url = fields.Char(string='Image URL', help='Public URL after upload to imgbb')

    # Channels
    channel_ids = fields.Many2many(
        'c21.social.channel',
        string='Publish Channels',
        default=lambda self: self.env['c21.social.channel'].search([('active', '=', True)])
    )

    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('posted', 'Posted'),
        ('failed', 'Failed'),
    ], string='State', default='draft', tracking=True)

    scheduled_time = fields.Datetime(string='Scheduled Time')
    posted_time = fields.Datetime(string='Posted Time')

    # Buffer response
    buffer_response = fields.Text(string='Buffer Response')
    error_message = fields.Text(string='Error Message')

    # Source news
    news_ids = fields.Many2many('c21.social.news', string='Related News')

    # Auto-generated flag
    is_auto_generated = fields.Boolean(string='Auto Generated', default=False)

    @api.depends('headline_zh', 'create_date')
    def _compute_name(self):
        for post in self:
            date_str = post.create_date.strftime('%Y%m%d-%H%M') if post.create_date else ''
            post.name = f"{post.headline_zh[:20]}... ({date_str})" if post.headline_zh else f"New Post ({date_str})"

    @api.onchange('headline_zh', 'data_point', 'background_color')
    def _onchange_regenerate_preview(self):
        """Auto-regenerate image preview when content or style changes"""
        if self.headline_zh and self.state == 'draft':
            try:
                from ..utils import image_generator
                self.image = image_generator.generate_post_image(
                    headline=self.headline_zh,
                    data_point=self.data_point or '',
                    background_color=self.background_color or 'navy_blue',
                )
            except Exception as e:
                _logger.warning(f"Preview generation failed: {e}")

    # === Actions ===

    def action_generate_image(self):
        """Generate branded image using PIL"""
        self.ensure_one()
        from ..utils import image_generator

        try:
            image_data = image_generator.generate_post_image(
                headline=self.headline_zh,
                data_point=self.data_point or '',
                background_color=self.background_color,
            )
            self.write({
                'image': image_data,
                'image_filename': f"c21-post-{fields.Datetime.now().strftime('%Y%m%d-%H%M%S')}.png",
                'image_url': False,  # Clear old URL so it gets re-uploaded
            })
            # Reload the form to show the new image
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'c21.social.post',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception as e:
            _logger.exception("Image generation failed")
            raise UserError(_("Image generation failed: %s") % str(e))

    def action_generate_captions(self):
        """Generate captions using AI"""
        self.ensure_one()
        from ..utils import ai_generator

        ICP = self.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('c21_social_marketing.openrouter_api_key')

        if not api_key:
            raise UserError(_('Please configure OpenRouter API Key in Settings'))

        try:
            # Get news content
            news_content = '\n'.join([
                f"[{n.source}] {n.name}: {n.description or ''}"
                for n in self.news_ids
            ]) if self.news_ids else self.headline_zh

            captions = ai_generator.generate_captions(api_key, news_content)

            self.write({
                'headline_zh': captions.get('headline_zh', self.headline_zh),
                'data_point': captions.get('data_point', self.data_point),
                'district': captions.get('district', self.district),
                'ig_caption': captions.get('ig_caption', ''),
                'fb_caption': captions.get('fb_caption', ''),
                'threads_caption': captions.get('threads_caption', ''),
                'source': captions.get('source', self.source),
                'background_color': captions.get('background_color', 'navy_blue'),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Captions generated successfully'),
                    'type': 'success',
                }
            }
        except Exception as e:
            _logger.exception("Caption generation failed")
            raise UserError(_("Caption generation failed: %s") % str(e))

    def action_submit_for_approval(self):
        """Submit for approval"""
        self.ensure_one()
        if not self.image:
            raise UserError(_('Please generate an image first'))
        if not self.ig_caption and not self.fb_caption and not self.threads_caption:
            raise UserError(_('Please generate captions first'))
        self.state = 'pending'

    def action_approve(self):
        """Approve the post"""
        self.ensure_one()
        self.state = 'approved'

    def action_reject(self):
        """Reject back to draft"""
        self.ensure_one()
        self.state = 'draft'

    def action_send_to_buffer(self):
        """Send post to Buffer"""
        self.ensure_one()
        if self.state not in ('approved', 'scheduled'):
            raise UserError(_('Can only send approved posts'))

        from ..utils import buffer_api, image_generator

        ICP = self.env['ir.config_parameter'].sudo()
        api_token = ICP.get_param('c21_social_marketing.buffer_api_token')
        imgbb_key = ICP.get_param('c21_social_marketing.imgbb_api_key')

        if not api_token:
            raise UserError(_('Please configure Buffer API Token in Settings'))

        # Check if any Instagram channel requires an image
        has_instagram = any(c.platform == 'instagram' for c in self.channel_ids)
        if has_instagram and not self.image:
            raise UserError(_('Instagram posts require an image'))

        try:
            # Upload image to imgbb if needed
            if self.image and not self.image_url:
                if not imgbb_key:
                    raise UserError(_('Please configure imgbb API Key in Settings'))
                _logger.info(f"Uploading image to imgbb for post {self.id}")
                image_data = self.image
                # Handle bytes if needed
                if isinstance(image_data, bytes):
                    image_data = image_data.decode('utf-8')
                self.image_url = image_generator.upload_to_imgbb(imgbb_key, image_data)
                _logger.info(f"Image uploaded: {self.image_url}")

            # Verify we have image URL for Instagram
            if has_instagram and not self.image_url:
                raise UserError(_('Image upload failed, please try again'))

            # Send to each channel
            results = []
            for channel in self.channel_ids:
                caption = ''
                if channel.platform == 'instagram':
                    caption = self._format_ig_caption()
                elif channel.platform == 'facebook':
                    caption = self._format_fb_caption()
                elif channel.platform == 'threads':
                    caption = self._format_threads_caption()

                _logger.info(f"Sending to Buffer channel: {channel.name} ({channel.platform})")
                result = buffer_api.create_post(
                    api_token=api_token,
                    channel_id=channel.buffer_channel_id,
                    text=caption,
                    image_url=self.image_url if channel.include_image else None,
                    platform=channel.platform,
                )
                results.append({
                    'channel': channel.name,
                    'result': result
                })
                _logger.info(f"Buffer response for {channel.name}: {result}")

                # Update channel last post time
                channel.last_post_time = fields.Datetime.now()

            self.write({
                'state': 'scheduled',
                'buffer_response': json.dumps(results, indent=2, ensure_ascii=False),
                'scheduled_time': fields.Datetime.now(),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Sent to %d channels') % len(results),
                    'type': 'success',
                }
            }
        except UserError:
            raise
        except Exception as e:
            _logger.exception("Buffer posting failed")
            self.write({
                'state': 'failed',
                'error_message': str(e),
            })
            raise UserError(_("Send failed: %s") % str(e))

    def _format_ig_caption(self):
        """Format Instagram caption with hashtags"""
        caption = self.ig_caption or self.headline_zh
        hashtags = "#香港地產 #寫字樓 #商用樓 #地產新聞 #C21HK #HongKongProperty"
        return f"{caption}\n\n{hashtags}"

    def _format_fb_caption(self):
        """Format Facebook caption with source"""
        caption = self.fb_caption or self.headline_zh
        source_line = f"\n\nSource: {self.source}" if self.source else ""
        hashtags = "\n\n#香港地產 #寫字樓 #商用樓"
        return f"{caption}{source_line}{hashtags}"

    def _format_threads_caption(self):
        """Format Threads caption"""
        return self.threads_caption or self.headline_zh

    # === Scheduled Actions ===

    @api.model
    def cron_fetch_news(self):
        """Scheduled: Fetch news from all active feeds"""
        from ..utils import rss_scraper
        feeds = self.env['c21.social.feed'].search([('active', '=', True)])
        for feed in feeds:
            try:
                rss_scraper.fetch_feed(self.env, feed)
            except Exception as e:
                _logger.exception(f"Failed to fetch feed {feed.name}")

    @api.model
    def cron_generate_post(self):
        """Scheduled: Generate a new post from recent news"""
        from ..utils import rss_scraper, ai_generator, image_generator

        ICP = self.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('c21_social_marketing.openrouter_api_key')
        auto_approve = ICP.get_param('c21_social_marketing.auto_approve', 'False') == 'True'

        if not api_key:
            _logger.warning("OpenRouter API key not configured, skipping post generation")
            return

        # Get unused property news from today
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        news_items = self.env['c21.social.news'].search([
            ('is_property_news', '=', True),
            ('used', '=', False),
            ('fetch_date', '>=', today_start),
        ], limit=10, order='relevance_score desc, fetch_date desc')

        if not news_items:
            _logger.info("No new property news to generate post from")
            return

        try:
            # Combine news for AI
            news_text = '\n'.join([
                f"[{n.source}] {n.name}: {n.description or ''}"
                for n in news_items
            ])

            # Generate captions
            captions = ai_generator.generate_captions(api_key, news_text)

            # Generate image
            image_data = image_generator.generate_post_image(
                headline=captions.get('headline_zh', ''),
                data_point=captions.get('data_point', ''),
                background_color=captions.get('background_color', 'navy_blue'),
            )

            # Create post
            channels = self.env['c21.social.channel'].search([('active', '=', True)])
            post = self.create({
                'headline_zh': captions.get('headline_zh', ''),
                'data_point': captions.get('data_point', ''),
                'district': captions.get('district', ''),
                'source': captions.get('source', ''),
                'ig_caption': captions.get('ig_caption', ''),
                'fb_caption': captions.get('fb_caption', ''),
                'threads_caption': captions.get('threads_caption', ''),
                'background_color': captions.get('background_color', 'navy_blue'),
                'image': image_data,
                'image_filename': f"c21-post-{fields.Datetime.now().strftime('%Y%m%d-%H%M%S')}.png",
                'channel_ids': [(6, 0, channels.ids)],
                'news_ids': [(6, 0, news_items.ids)],
                'is_auto_generated': True,
                'state': 'approved' if auto_approve else 'pending',
            })

            # Mark news as used
            news_items.write({'used': True})

            _logger.info(f"Auto-generated post: {post.name}")

            # Auto-send if configured
            auto_send = ICP.get_param('c21_social_marketing.auto_send', 'False') == 'True'
            if auto_send and post.state == 'approved':
                post.action_send_to_buffer()

        except Exception as e:
            _logger.exception("Failed to auto-generate post")
