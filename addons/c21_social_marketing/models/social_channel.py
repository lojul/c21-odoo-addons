# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SocialChannel(models.Model):
    _name = 'c21.social.channel'
    _description = 'Social Media Channel'
    _order = 'sequence, name'

    name = fields.Char(string='名稱', required=True)
    platform = fields.Selection([
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('threads', 'Threads'),
    ], string='平台', required=True)
    buffer_channel_id = fields.Char(string='Buffer Channel ID', required=True)
    active = fields.Boolean(string='啟用', default=True)
    sequence = fields.Integer(string='排序', default=10)

    # Stats
    last_post_time = fields.Datetime(string='上次發文')
    post_count = fields.Integer(string='發文數量', compute='_compute_post_count')

    # Platform-specific settings
    include_image = fields.Boolean(string='包含圖片', default=True)
    hashtags = fields.Text(string='預設標籤', help='Platform-specific hashtags')

    @api.depends('name')
    def _compute_post_count(self):
        for channel in self:
            # Count posts that include this channel
            channel.post_count = self.env['c21.social.post'].search_count([
                ('channel_ids', 'in', channel.id),
                ('state', '=', 'posted')
            ])

    def get_platform_icon(self):
        icons = {
            'instagram': 'fa-instagram',
            'facebook': 'fa-facebook',
            'threads': 'fa-at',
        }
        return icons.get(self.platform, 'fa-share-alt')
