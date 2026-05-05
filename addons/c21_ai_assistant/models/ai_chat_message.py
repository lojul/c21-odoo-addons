# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json


class AiChatMessage(models.Model):
    _name = 'ai.chat.message'
    _description = 'AI Chat Message'
    _order = 'create_date asc'

    session_id = fields.Many2one(
        'ai.chat.session',
        string='Session',
        required=True,
        ondelete='cascade',
        index=True)

    user_id = fields.Many2one(
        related='session_id.user_id',
        store=True,
        string='User')

    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ], string='Role', required=True, index=True)

    content = fields.Text(
        string='Content',
        required=True)

    # Metadata
    intent = fields.Selection([
        ('property_search', 'Property Search'),
        ('crm_search', 'CRM Search'),
        ('document_search', 'Document Search'),
        ('news_search', 'News Search'),
        ('general', 'General Q&A'),
        ('greeting', 'Greeting'),
        ('rejected', 'Rejected (Off-topic)'),
        ('unknown', 'Unknown'),
    ], string='Intent')

    # For assistant messages
    model_used = fields.Char(string='Model Used')
    tokens_used = fields.Integer(string='Tokens Used', default=0)
    response_time = fields.Float(string='Response Time (s)')

    # Search results metadata
    search_results = fields.Text(
        string='Search Results',
        help='JSON serialized search results')

    sources = fields.Text(
        string='Sources',
        help='JSON serialized source references')

    # Error tracking
    is_error = fields.Boolean(string='Is Error', default=False)
    error_message = fields.Text(string='Error Message')

    def get_search_results(self):
        """Parse and return search results"""
        self.ensure_one()
        if self.search_results:
            try:
                return json.loads(self.search_results)
            except json.JSONDecodeError:
                return []
        return []

    def set_search_results(self, results):
        """Serialize and store search results"""
        self.ensure_one()
        self.write({'search_results': json.dumps(results, ensure_ascii=False)})

    def get_sources(self):
        """Parse and return sources"""
        self.ensure_one()
        if self.sources:
            try:
                return json.loads(self.sources)
            except json.JSONDecodeError:
                return []
        return []

    def set_sources(self, sources):
        """Serialize and store sources"""
        self.ensure_one()
        self.write({'sources': json.dumps(sources, ensure_ascii=False)})

    @api.model
    def create_user_message(self, session, content):
        """Helper to create a user message"""
        return self.create({
            'session_id': session.id,
            'role': 'user',
            'content': content,
        })

    @api.model
    def create_assistant_message(self, session, content, intent=None,
                                  model_used=None, tokens_used=0,
                                  response_time=0, search_results=None,
                                  sources=None):
        """Helper to create an assistant message"""
        values = {
            'session_id': session.id,
            'role': 'assistant',
            'content': content,
            'intent': intent,
            'model_used': model_used,
            'tokens_used': tokens_used,
            'response_time': response_time,
        }
        if search_results:
            values['search_results'] = json.dumps(search_results, ensure_ascii=False)
        if sources:
            values['sources'] = json.dumps(sources, ensure_ascii=False)

        message = self.create(values)

        # Update session stats
        if tokens_used:
            session.write({'total_tokens': session.total_tokens + tokens_used})

        return message

    @api.model
    def create_error_message(self, session, error_message):
        """Helper to create an error message"""
        return self.create({
            'session_id': session.id,
            'role': 'assistant',
            'content': _('Sorry, an error occurred while processing your request. Please try again later.'),
            'is_error': True,
            'error_message': error_message,
        })
