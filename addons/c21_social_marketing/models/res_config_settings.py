# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # API Keys
    social_openrouter_api_key = fields.Char(
        string='OpenRouter API Key',
        config_parameter='c21_social_marketing.openrouter_api_key',
        help='API key for OpenRouter (DeepSeek, etc.)'
    )
    social_buffer_api_token = fields.Char(
        string='Buffer API Token',
        config_parameter='c21_social_marketing.buffer_api_token',
        help='Buffer API token for posting'
    )
    social_imgbb_api_key = fields.Char(
        string='imgbb API Key',
        config_parameter='c21_social_marketing.imgbb_api_key',
        help='imgbb API key for image hosting'
    )

    # AI Settings
    social_ai_model = fields.Char(
        string='AI Model',
        config_parameter='c21_social_marketing.ai_model',
        help='OpenRouter model ID (e.g., deepseek/deepseek-chat)'
    )

    # Automation
    social_auto_approve = fields.Boolean(
        string='自動審批',
        config_parameter='c21_social_marketing.auto_approve',
        help='Auto-approve generated posts (skip pending state)'
    )
    social_auto_send = fields.Boolean(
        string='自動發送',
        config_parameter='c21_social_marketing.auto_send',
        help='Auto-send approved posts to Buffer'
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        # Set default AI model if not configured
        ai_model = ICP.get_param('c21_social_marketing.ai_model', 'deepseek/deepseek-chat')
        res['social_ai_model'] = ai_model
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        # Ensure AI model has a default
        if not self.social_ai_model:
            ICP.set_param('c21_social_marketing.ai_model', 'deepseek/deepseek-chat')
