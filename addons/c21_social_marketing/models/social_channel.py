# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SocialChannel(models.Model):
    _name = 'c21.social.channel'
    _description = 'Social Media Channel'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    platform = fields.Selection([
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('threads', 'Threads'),
    ], string='Platform', required=True)
    buffer_channel_id = fields.Char(string='Buffer Channel ID', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)

    # Stats
    last_post_time = fields.Datetime(string='Last Post Time')
    post_count = fields.Integer(string='Post Count', compute='_compute_post_count')

    # Platform-specific settings
    include_image = fields.Boolean(string='Include Image', default=True)
    hashtags = fields.Text(string='Default Hashtags', help='Platform-specific hashtags')

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
