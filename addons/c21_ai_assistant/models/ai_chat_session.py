# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta
import uuid


class AiChatSession(models.Model):
    _name = 'ai.chat.session'
    _description = 'AI Chat Session'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    session_id = fields.Char(
        string='Session ID',
        required=True,
        index=True,
        default=lambda self: str(uuid.uuid4()),
        readonly=True)

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        index=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company)

    display_name = fields.Char(
        string='Name',
        compute='_compute_display_name',
        store=True)

    message_ids = fields.One2many(
        'ai.chat.message',
        'session_id',
        string='Messages')

    message_count = fields.Integer(
        string='Message Count',
        compute='_compute_message_count',
        store=True)

    last_activity = fields.Datetime(
        string='Last Activity',
        default=fields.Datetime.now)

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('closed', 'Closed'),
    ], string='State', default='active', index=True)

    summary = fields.Text(
        string='Summary',
        help='Auto-generated summary of the conversation')

    # Memory/Context for follow-up queries
    last_search_context = fields.Text(
        string='Last Search Context',
        help='JSON data about the last search for follow-up queries')

    # Statistics
    total_tokens = fields.Integer(
        string='Total Tokens',
        default=0)

    property_searches = fields.Integer(
        string='Property Searches',
        default=0)

    crm_searches = fields.Integer(
        string='CRM Searches',
        default=0)

    rag_searches = fields.Integer(
        string='Document Searches',
        default=0)

    news_searches = fields.Integer(
        string='News Searches',
        default=0)

    @api.depends('user_id', 'create_date')
    def _compute_display_name(self):
        for record in self:
            date_str = record.create_date.strftime('%Y-%m-%d %H:%M') if record.create_date else ''
            record.display_name = f"{record.user_id.name} - {date_str}"

    @api.depends('message_ids')
    def _compute_message_count(self):
        for record in self:
            record.message_count = len(record.message_ids)

    def action_close(self):
        """Close the session"""
        self.write({'state': 'closed'})

    def action_reopen(self):
        """Reopen a closed session"""
        self.write({
            'state': 'active',
            'last_activity': fields.Datetime.now()
        })

    @api.model
    def get_or_create_session(self, session_id=None):
        """Get existing session or create new one"""
        if session_id:
            session = self.search([
                ('session_id', '=', session_id),
                ('user_id', '=', self.env.user.id),
                ('state', '=', 'active')
            ], limit=1)
            if session:
                # Check if session has expired
                timeout = int(self.env['ir.config_parameter'].sudo().get_param(
                    'c21_ai_assistant.session_timeout', '30'))
                if session.last_activity:
                    expiry_time = session.last_activity + timedelta(minutes=timeout)
                    if fields.Datetime.now() > expiry_time:
                        session.write({'state': 'expired'})
                        session = None
                    else:
                        session.write({'last_activity': fields.Datetime.now()})
                        return session

        # Create new session
        return self.create({
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
        })

    @api.model
    def cleanup_expired_sessions(self):
        """Cron job to mark expired sessions"""
        timeout = int(self.env['ir.config_parameter'].sudo().get_param(
            'c21_ai_assistant.session_timeout', '30'))
        expiry_time = fields.Datetime.now() - timedelta(minutes=timeout)

        expired = self.search([
            ('state', '=', 'active'),
            ('last_activity', '<', expiry_time)
        ])
        expired.write({'state': 'expired'})
        return True

    def get_conversation_history(self, limit=10):
        """Get recent messages for context"""
        self.ensure_one()
        messages = self.message_ids.sorted('create_date', reverse=True)[:limit]
        return [{
            'role': msg.role,
            'content': msg.content,
        } for msg in reversed(messages)]

    def increment_stat(self, stat_type):
        """Increment search statistics"""
        self.ensure_one()
        field_map = {
            'property': 'property_searches',
            'crm': 'crm_searches',
            'rag': 'rag_searches',
            'news': 'news_searches',
        }
        if stat_type in field_map:
            self.write({field_map[stat_type]: self[field_map[stat_type]] + 1})

    def set_search_context(self, context_type, results, query):
        """Store last search context for follow-up queries"""
        import json
        self.ensure_one()
        context = {
            'type': context_type,
            'query': query,
            'results': results[:5] if results else [],  # Store top 5 results
            'count': len(results) if results else 0,
        }
        self.write({'last_search_context': json.dumps(context, ensure_ascii=False)})

    def get_search_context(self):
        """Get last search context"""
        import json
        self.ensure_one()
        if self.last_search_context:
            try:
                return json.loads(self.last_search_context)
            except json.JSONDecodeError:
                return None
        return None
