# -*- coding: utf-8 -*-

import requests
import logging
import time

_logger = logging.getLogger(__name__)


class RAGService:
    """Service for interacting with n8n RAG workflow"""

    def __init__(self, env):
        self.env = env
        self._load_config()

    def _load_config(self):
        """Load configuration from ir.config_parameter"""
        ICP = self.env['ir.config_parameter'].sudo()

        self.enabled = ICP.get_param('c21_ai_assistant.rag_enabled', 'True') == 'True'
        self.endpoint = ICP.get_param('c21_ai_assistant.rag_endpoint', '')
        self.api_key = ICP.get_param('c21_ai_assistant.rag_api_key', '')
        self.debug_mode = ICP.get_param('c21_ai_assistant.debug_mode', 'False') == 'True'

    def is_available(self):
        """Check if RAG service is configured and enabled"""
        return self.enabled and bool(self.endpoint)

    def search(self, question, session_id=None):
        """
        Search property documents using n8n RAG workflow

        Args:
            question: User's question
            session_id: Optional session ID for conversation context

        Returns:
            dict with 'answer', 'sources', 'images', 'stats', or error info
        """
        if not self.is_available():
            return {
                'error': 'RAG service not configured',
                'answer': None,
                'sources': [],
            }

        start_time = time.time()

        if self.debug_mode:
            _logger.info(f"[AI Assistant RAG] Searching: {question[:100]}...")

        try:
            headers = {
                "Content-Type": "application/json",
            }

            # Add API key if configured
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {
                "question": question,
                "session_id": session_id or f"odoo_{self.env.user.id}_{int(time.time())}"
            }

            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            result = {
                'answer': data.get('answer', ''),
                'sources': data.get('sources', []),
                'images': data.get('images', []),
                'stats': data.get('stats', {}),
                'response_time': time.time() - start_time,
            }

            if self.debug_mode:
                _logger.info(f"[AI Assistant RAG] Found {len(result['sources'])} sources "
                           f"in {result['response_time']:.2f}s")

            return result

        except requests.exceptions.Timeout:
            _logger.error("[AI Assistant RAG] Request timeout")
            return {
                'error': 'RAG service timeout',
                'answer': None,
                'sources': [],
                'response_time': time.time() - start_time,
            }
        except requests.exceptions.RequestException as e:
            _logger.error(f"[AI Assistant RAG] Request error: {str(e)}")
            return {
                'error': f'RAG service error: {str(e)}',
                'answer': None,
                'sources': [],
                'response_time': time.time() - start_time,
            }
        except Exception as e:
            _logger.error(f"[AI Assistant RAG] Unexpected error: {str(e)}")
            return {
                'error': f'Unexpected error: {str(e)}',
                'answer': None,
                'sources': [],
                'response_time': time.time() - start_time,
            }

    def format_sources_for_display(self, sources):
        """Format RAG sources for display in chat"""
        if not sources:
            return ""

        lines = ["\n\n**來源:**"]
        for src in sources[:5]:  # Limit to top 5 sources
            file_name = src.get('fileName', 'Unknown')
            pages = src.get('pages', [])
            doc_type = src.get('docType', '')

            if pages:
                page_str = f", 頁 {', '.join(map(str, pages[:3]))}"
                if len(pages) > 3:
                    page_str += "..."
            else:
                page_str = ""

            type_str = f" ({doc_type})" if doc_type else ""
            lines.append(f"- {file_name}{page_str}{type_str}")

        return "\n".join(lines)

    def format_context_for_llm(self, rag_result):
        """Format RAG result as context for LLM"""
        if not rag_result or rag_result.get('error'):
            return ""

        context_parts = []

        if rag_result.get('answer'):
            context_parts.append(f"Document search result:\n{rag_result['answer']}")

        if rag_result.get('sources'):
            sources_info = []
            for src in rag_result['sources'][:5]:
                file_name = src.get('fileName', 'Unknown')
                pages = src.get('pages', [])
                key_topics = src.get('keyTopics', '')
                sources_info.append(f"- {file_name} (pages: {pages}, topics: {key_topics})")
            if sources_info:
                context_parts.append("Sources:\n" + "\n".join(sources_info))

        return "\n\n".join(context_parts)
