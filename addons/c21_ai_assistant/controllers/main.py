# -*- coding: utf-8 -*-

import json
import logging

from odoo import http
from odoo.http import request

from ..services.orchestrator import Orchestrator

_logger = logging.getLogger(__name__)


class AiAssistantController(http.Controller):
    """REST API controller for AI Assistant"""

    @http.route('/ai_assistant/chat', type='jsonrpc', auth='user', methods=['POST'])
    def chat(self, message, session_id=None):
        """
        Main chat endpoint

        Args:
            message: User's message text
            session_id: Optional session ID for continuing conversation

        Returns:
            dict with response data
        """
        try:
            # Get or create session
            Session = request.env['ai.chat.session']
            session = Session.get_or_create_session(session_id)

            # Get conversation history
            conversation_history = session.get_conversation_history(limit=10)

            # Create user message
            Message = request.env['ai.chat.message']
            user_msg = Message.create_user_message(session, message)

            # Process query
            orchestrator = Orchestrator(request.env)
            result = orchestrator.process_query(
                message,
                session,
                conversation_history
            )

            # Create assistant message
            assistant_msg = Message.create_assistant_message(
                session,
                result['response'],
                intent=result.get('intent'),
                model_used=result.get('model'),
                tokens_used=result.get('tokens', 0),
                response_time=result.get('response_time', 0),
                search_results=result.get('search_results'),
                sources=result.get('sources'),
            )

            return {
                'success': True,
                'session_id': session.session_id,
                'message_id': assistant_msg.id,
                'response': result['response'],
                'intent': result.get('intent'),
                'search_results': result.get('search_results', []),
                'sources': result.get('sources', []),
                'model': result.get('model'),
                'tokens': result.get('tokens', 0),
                'response_time': result.get('response_time', 0),
            }

        except Exception as e:
            _logger.error(f"[AI Assistant] Chat error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'response': '抱歉，處理您的請求時發生錯誤。請稍後再試。',
            }

    @http.route('/ai_assistant/session/new', type='jsonrpc', auth='user', methods=['POST'])
    def new_session(self):
        """Create a new chat session"""
        try:
            Session = request.env['ai.chat.session']
            session = Session.create({
                'user_id': request.env.user.id,
                'company_id': request.env.company.id,
            })

            # Get welcome message
            ICP = request.env['ir.config_parameter'].sudo()
            welcome = ICP.get_param('c21_ai_assistant.welcome_message', '')

            return {
                'success': True,
                'session_id': session.session_id,
                'welcome_message': welcome,
            }

        except Exception as e:
            _logger.error(f"[AI Assistant] New session error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    @http.route('/ai_assistant/session/history', type='jsonrpc', auth='user', methods=['POST'])
    def get_history(self, session_id):
        """Get chat history for a session"""
        try:
            Session = request.env['ai.chat.session']
            session = Session.search([
                ('session_id', '=', session_id),
                ('user_id', '=', request.env.user.id),
            ], limit=1)

            if not session:
                return {
                    'success': False,
                    'error': 'Session not found',
                }

            messages = []
            for msg in session.message_ids.sorted('create_date'):
                messages.append({
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.create_date.isoformat() if msg.create_date else None,
                    'intent': msg.intent,
                    'is_error': msg.is_error,
                })

            return {
                'success': True,
                'session_id': session_id,
                'messages': messages,
                'state': session.state,
            }

        except Exception as e:
            _logger.error(f"[AI Assistant] Get history error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    @http.route('/ai_assistant/session/close', type='jsonrpc', auth='user', methods=['POST'])
    def close_session(self, session_id):
        """Close a chat session"""
        try:
            Session = request.env['ai.chat.session']
            session = Session.search([
                ('session_id', '=', session_id),
                ('user_id', '=', request.env.user.id),
            ], limit=1)

            if session:
                session.action_close()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Session not found'}

        except Exception as e:
            _logger.error(f"[AI Assistant] Close session error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    @http.route('/ai_assistant/sessions', type='jsonrpc', auth='user', methods=['POST'])
    def list_sessions(self, limit=10):
        """List user's recent chat sessions"""
        try:
            Session = request.env['ai.chat.session']
            sessions = Session.search([
                ('user_id', '=', request.env.user.id),
            ], order='create_date desc', limit=limit)

            result = []
            for session in sessions:
                # Get first user message as preview
                preview = ''
                first_msg = session.message_ids.filtered(
                    lambda m: m.role == 'user'
                ).sorted('create_date')[:1]
                if first_msg:
                    preview = first_msg.content[:100]

                result.append({
                    'session_id': session.session_id,
                    'state': session.state,
                    'message_count': session.message_count,
                    'preview': preview,
                    'create_date': session.create_date.isoformat() if session.create_date else None,
                    'last_activity': session.last_activity.isoformat() if session.last_activity else None,
                })

            return {
                'success': True,
                'sessions': result,
            }

        except Exception as e:
            _logger.error(f"[AI Assistant] List sessions error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    @http.route('/ai_assistant/config', type='jsonrpc', auth='user', methods=['POST'])
    def get_config(self):
        """Get client-side configuration"""
        try:
            ICP = request.env['ir.config_parameter'].sudo()

            # Check if user has access
            has_access = request.env.user.has_group(
                'c21_ai_assistant.group_ai_assistant_user')

            return {
                'success': True,
                'has_access': has_access,
                'welcome_message': ICP.get_param('c21_ai_assistant.welcome_message', ''),
                'features': {
                    'property_search': ICP.get_param(
                        'c21_ai_assistant.property_search_enabled', 'True') == 'True',
                    'crm_search': ICP.get_param(
                        'c21_ai_assistant.crm_search_enabled', 'True') == 'True',
                    'document_search': ICP.get_param(
                        'c21_ai_assistant.rag_enabled', 'True') == 'True',
                    'general_qa': ICP.get_param(
                        'c21_ai_assistant.general_qa_enabled', 'True') == 'True',
                },
            }

        except Exception as e:
            _logger.error(f"[AI Assistant] Get config error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }
