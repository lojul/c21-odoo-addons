# -*- coding: utf-8 -*-

import logging
import re
import time

from .llm_service import LLMService
from .rag_service import RAGService
from .search_service import SearchService

_logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator that routes user queries to appropriate services
    and combines results for the final response.
    """

    # Intent detection patterns
    INTENT_PATTERNS = {
        'property_search': [
            r'物業|property|properties|listing|listings',
            r'寫字樓|辦公室|office|offices',
            r'商舖|零售|retail|shop',
            r'工業|industrial|warehouse',
            r'cowork|共享|flexible',
            r'租金|rent|lease|出租',
            r'面積|sqft|呎|平方',
            r'搜尋|找|search|find|show|list',
        ],
        'crm_search': [
            r'客戶|customer|client',
            r'潛在客戶|lead|leads|prospect',
            r'聯絡人|contact|contacts',
            r'銷售|sales|deal',
            r'pipeline|管道',
        ],
        'document_search': [
            r'文件|document|file|pdf',
            r'particular|particulars|詳情',
            r'合約|contract|agreement',
            r'資料|information|details',
        ],
        'greeting': [
            r'^(hi|hello|hey|你好|哈囉|早晨|午安|晚安)',
            r'^(help|幫助|怎麼用)',
        ],
    }

    def __init__(self, env):
        self.env = env
        self._load_config()

        # Initialize services
        self.llm_service = LLMService(env)
        self.rag_service = RAGService(env)
        self.search_service = SearchService(env)

    def _load_config(self):
        """Load configuration from ir.config_parameter"""
        ICP = self.env['ir.config_parameter'].sudo()

        self.property_search_enabled = ICP.get_param(
            'c21_ai_assistant.property_search_enabled', 'True') == 'True'
        self.crm_search_enabled = ICP.get_param(
            'c21_ai_assistant.crm_search_enabled', 'True') == 'True'
        self.rag_enabled = ICP.get_param(
            'c21_ai_assistant.rag_enabled', 'True') == 'True'
        self.general_qa_enabled = ICP.get_param(
            'c21_ai_assistant.general_qa_enabled', 'True') == 'True'
        self.debug_mode = ICP.get_param(
            'c21_ai_assistant.debug_mode', 'False') == 'True'

    def detect_intent(self, query):
        """
        Detect the intent of a user query

        Returns:
            str: One of 'property_search', 'crm_search', 'document_search',
                 'greeting', 'general'
        """
        query_lower = query.lower()

        # Check each intent pattern
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    if self.debug_mode:
                        _logger.info(f"[AI Assistant] Detected intent: {intent} (pattern: {pattern})")
                    return intent

        return 'general'

    def process_query(self, query, session, conversation_history=None):
        """
        Process a user query and return a response

        Args:
            query: User's question/request
            session: ai.chat.session record
            conversation_history: Optional list of previous messages

        Returns:
            dict with 'response', 'intent', 'search_results', 'sources',
                       'model', 'tokens', 'response_time'
        """
        start_time = time.time()

        # Detect intent
        intent = self.detect_intent(query)

        if self.debug_mode:
            _logger.info(f"[AI Assistant] Processing query: {query[:100]}... (intent: {intent})")

        # Handle based on intent
        if intent == 'greeting':
            return self._handle_greeting(query, start_time)

        if intent == 'property_search' and self.property_search_enabled:
            return self._handle_property_search(query, session, conversation_history, start_time)

        if intent == 'crm_search' and self.crm_search_enabled:
            return self._handle_crm_search(query, session, conversation_history, start_time)

        if intent == 'document_search' and self.rag_enabled:
            return self._handle_document_search(query, session, start_time)

        if self.general_qa_enabled:
            return self._handle_general_query(query, session, conversation_history, start_time)

        # Fallback if no handler available
        return {
            'response': "抱歉，目前無法處理您的請求。請嘗試其他問題。",
            'intent': intent,
            'search_results': [],
            'sources': [],
            'model': None,
            'tokens': 0,
            'response_time': time.time() - start_time,
        }

    def _handle_greeting(self, query, start_time):
        """Handle greeting messages"""
        ICP = self.env['ir.config_parameter'].sudo()
        welcome = ICP.get_param('c21_ai_assistant.welcome_message', '')

        if not welcome:
            welcome = """你好！我是 C21 AI 助手。我可以幫你：
- 搜尋物業資料
- 查詢 CRM 客戶/潛在客戶
- 搜尋物業文件
- 回答一般問題

請問有什麼可以幫到你？"""

        return {
            'response': welcome,
            'intent': 'greeting',
            'search_results': [],
            'sources': [],
            'model': None,
            'tokens': 0,
            'response_time': time.time() - start_time,
        }

    def _handle_property_search(self, query, session, conversation_history, start_time):
        """Handle property search queries"""
        # Extract search parameters
        params = self.search_service.extract_search_params(query)

        # Search properties
        search_result = self.search_service.search_properties(
            params.get('search_term', query),
            params.get('filters', {})
        )

        # Increment session stat
        session.increment_stat('property')

        # If we have results, format them
        if search_result.get('results'):
            formatted = search_result.get('formatted', '')

            # Optionally use LLM to enhance the response
            if len(search_result['results']) > 0:
                # Build context from search results
                context = f"Property search results:\n{formatted}"

                messages = conversation_history or []
                messages.append({'role': 'user', 'content': query})

                llm_result = self.llm_service.chat(messages, context=context)

                return {
                    'response': llm_result.get('content', formatted),
                    'intent': 'property_search',
                    'search_results': search_result['results'],
                    'sources': [],
                    'model': llm_result.get('model'),
                    'tokens': llm_result.get('tokens_used', 0),
                    'response_time': time.time() - start_time,
                }

        # No results - use LLM to respond
        messages = conversation_history or []
        messages.append({'role': 'user', 'content': query})

        llm_result = self.llm_service.chat(
            messages,
            context="No properties found matching the search criteria."
        )

        return {
            'response': llm_result.get('content', '未找到符合條件的物業。'),
            'intent': 'property_search',
            'search_results': [],
            'sources': [],
            'model': llm_result.get('model'),
            'tokens': llm_result.get('tokens_used', 0),
            'response_time': time.time() - start_time,
        }

    def _handle_crm_search(self, query, session, conversation_history, start_time):
        """Handle CRM search queries"""
        # Determine if searching leads or partners
        model_type = 'lead'
        if any(word in query.lower() for word in ['聯絡人', 'contact', '客戶', 'customer']):
            model_type = 'partner'

        # Search CRM
        search_result = self.search_service.search_crm(query, model_type)

        # Increment session stat
        session.increment_stat('crm')

        # Format and respond
        if search_result.get('results'):
            formatted = search_result.get('formatted', '')
            context = f"CRM search results:\n{formatted}"

            messages = conversation_history or []
            messages.append({'role': 'user', 'content': query})

            llm_result = self.llm_service.chat(messages, context=context)

            return {
                'response': llm_result.get('content', formatted),
                'intent': 'crm_search',
                'search_results': search_result['results'],
                'sources': [],
                'model': llm_result.get('model'),
                'tokens': llm_result.get('tokens_used', 0),
                'response_time': time.time() - start_time,
            }

        return {
            'response': '未找到符合條件的 CRM 記錄。',
            'intent': 'crm_search',
            'search_results': [],
            'sources': [],
            'model': None,
            'tokens': 0,
            'response_time': time.time() - start_time,
        }

    def _handle_document_search(self, query, session, start_time):
        """Handle document search via RAG"""
        if not self.rag_service.is_available():
            return {
                'response': '文件搜尋功能目前不可用。請聯絡管理員設定 RAG 服務。',
                'intent': 'document_search',
                'search_results': [],
                'sources': [],
                'model': None,
                'tokens': 0,
                'response_time': time.time() - start_time,
            }

        # Call RAG service
        rag_result = self.rag_service.search(query, session.session_id)

        # Increment session stat
        session.increment_stat('rag')

        if rag_result.get('error'):
            return {
                'response': f"搜尋文件時發生錯誤: {rag_result['error']}",
                'intent': 'document_search',
                'search_results': [],
                'sources': [],
                'model': None,
                'tokens': 0,
                'response_time': time.time() - start_time,
            }

        # Format response with sources
        response = rag_result.get('answer', '未找到相關文件。')
        sources_text = self.rag_service.format_sources_for_display(rag_result.get('sources', []))
        if sources_text:
            response += sources_text

        return {
            'response': response,
            'intent': 'document_search',
            'search_results': [],
            'sources': rag_result.get('sources', []),
            'model': 'RAG',
            'tokens': 0,
            'response_time': time.time() - start_time,
        }

    def _handle_general_query(self, query, session, conversation_history, start_time):
        """Handle general queries using LLM"""
        messages = conversation_history or []
        messages.append({'role': 'user', 'content': query})

        # Optionally enrich with RAG context
        context = None
        sources = []

        if self.rag_enabled and self.rag_service.is_available():
            # Try to get relevant context from documents
            rag_result = self.rag_service.search(query, session.session_id)
            if not rag_result.get('error') and rag_result.get('sources'):
                context = self.rag_service.format_context_for_llm(rag_result)
                sources = rag_result.get('sources', [])
                session.increment_stat('rag')

        llm_result = self.llm_service.chat(messages, context=context)

        response = llm_result.get('content', '抱歉，無法處理您的請求。')

        # Add sources if we used RAG
        if sources:
            sources_text = self.rag_service.format_sources_for_display(sources)
            if sources_text:
                response += sources_text

        return {
            'response': response,
            'intent': 'general',
            'search_results': [],
            'sources': sources,
            'model': llm_result.get('model'),
            'tokens': llm_result.get('tokens_used', 0),
            'response_time': time.time() - start_time,
        }
