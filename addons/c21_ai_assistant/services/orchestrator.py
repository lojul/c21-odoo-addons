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
            # Follow-up requests for CRM records
            r'profile|檔案|個人資料',
            r'open\s+(his|her|their|the)|打開|查看',
            r'view\s+(his|her|their|the|profile)',
            r'show\s+(his|her|their|the|profile|me)',
        ],
        'document_search': [
            r'文件|document|file|pdf',
            r'particular|particulars|詳情',
            r'合約|contract|agreement',
            # Removed generic 'information|details' as it's too broad
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
        query_stripped = query.strip()

        # Check for person names FIRST (before other patterns)
        # Person names should go to CRM search, not property search
        # Pattern: "FirstName LastName" (case-insensitive) or Chinese name (2-4 chars)
        if re.match(r'^[A-Za-z]+\s+[A-Za-z]+$', query_stripped):
            if self.debug_mode:
                _logger.info(f"[AI Assistant] Detected intent: crm_search (person name)")
            return 'crm_search'
        if re.match(r'^[\u4e00-\u9fff]{2,4}$', query_stripped):
            if self.debug_mode:
                _logger.info(f"[AI Assistant] Detected intent: crm_search (Chinese name)")
            return 'crm_search'

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

        # For general queries, check if it's relevant to the business
        if self.general_qa_enabled and self._is_relevant_query(query):
            return self._handle_general_query(query, session, conversation_history, start_time)

        # Reject irrelevant questions
        return self._handle_irrelevant_query(query, start_time)

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
        query_lower = query.lower()

        # Check if this is a follow-up request (open/view/show profile)
        is_followup = any(word in query_lower for word in [
            'open', 'view', 'show', 'profile', '打開', '查看', '檔案'
        ])

        # Extract name from context if it's a follow-up request
        search_term = query
        if is_followup and conversation_history:
            # Look for a name in previous assistant responses
            for msg in reversed(conversation_history):
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '')
                    # Try multiple patterns to extract names
                    # Pattern 1: Bold markdown **Name**
                    name_match = re.search(r'\*\*([^*]+)\*\*', content)
                    if name_match:
                        search_term = name_match.group(1).strip()
                        if self.debug_mode:
                            _logger.info(f"[AI Assistant] Extracted name from bold: {search_term}")
                        break
                    # Pattern 2: "Name's" possessive form (e.g., "Stephen Wong's profile")
                    name_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'s", content)
                    if name_match:
                        search_term = name_match.group(1).strip()
                        if self.debug_mode:
                            _logger.info(f"[AI Assistant] Extracted name from possessive: {search_term}")
                        break
                    # Pattern 3: "found/找到 Name" pattern
                    name_match = re.search(r'(?:found|找到)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', content)
                    if name_match:
                        search_term = name_match.group(1).strip()
                        if self.debug_mode:
                            _logger.info(f"[AI Assistant] Extracted name from found pattern: {search_term}")
                        break
                # Also check user's previous query for the name
                elif msg.get('role') == 'user':
                    user_query = msg.get('content', '')
                    # Check if user searched for a name (e.g., "find Stephen Wong")
                    name_match = re.search(r'(?:find|search|找|查)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', user_query, re.IGNORECASE)
                    if name_match:
                        search_term = name_match.group(1).strip()
                        if self.debug_mode:
                            _logger.info(f"[AI Assistant] Extracted name from user query: {search_term}")
                        break

        # Determine if searching leads or partners
        # Default to partner for person name searches
        model_type = 'partner'  # Default to contacts
        if any(word in query_lower for word in ['lead', 'leads', '潛在客戶', 'prospect', 'opportunity', '商機']):
            model_type = 'lead'

        # Search CRM - try partners first, then leads if no results
        search_result = self.search_service.search_crm(search_term, model_type)

        # If no results found in partners, try leads
        if not search_result.get('results') and model_type == 'partner':
            search_result = self.search_service.search_crm(search_term, 'lead')
            if search_result.get('results'):
                model_type = 'lead'

        # Increment session stat
        session.increment_stat('crm')

        # Format and respond
        if search_result.get('results'):
            formatted = search_result.get('formatted', '')

            # If it's a follow-up request to open/view, provide direct links
            if is_followup and len(search_result['results']) == 1:
                record = search_result['results'][0]
                record_id = record.get('id')
                record_name = record.get('name', '')
                record_email = record.get('email', '')
                record_phone = record.get('phone', '')
                record_company = record.get('company', '')

                # Build a response with action link
                response_parts = [f"**{record_name}** 的個人資料:"]
                if record_company:
                    response_parts.append(f"公司: {record_company}")
                if record_email:
                    response_parts.append(f"電郵: {record_email}")
                if record_phone:
                    response_parts.append(f"電話: {record_phone}")

                model_name = 'crm.lead' if model_type == 'lead' else 'res.partner'
                response_parts.append(f"\n要在 Odoo 打開此記錄，請點擊: `/web#id={record_id}&model={model_name}&view_type=form`")

                return {
                    'response': '\n'.join(response_parts),
                    'intent': 'crm_search',
                    'search_results': search_result['results'],
                    'sources': [],
                    'model': None,
                    'tokens': 0,
                    'response_time': time.time() - start_time,
                }

            # Return formatted results directly (don't let LLM paraphrase)
            return {
                'response': formatted,
                'intent': 'crm_search',
                'search_results': search_result['results'],
                'sources': [],
                'model': None,
                'tokens': 0,
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

    def _is_relevant_query(self, query):
        """
        Check if a query is relevant to C21 business operations.
        Returns True for queries about properties, CRM, real estate, company operations,
        or queries that look like person name searches.
        """
        query_lower = query.lower()

        # Reject obvious off-topic queries FIRST
        irrelevant_patterns = [
            r'\b(python|javascript|java|coding|programming|code)\b',
            r'\b(recipe|cook|cooking|food)\b',
            r'\b(movie|film|music|song|game|gaming)\b',
            r'\b(weather|天氣)\b',
            r'\b(joke|笑話)\b',
            r'\b(translate|翻譯)\b',
            r'\b(math|calculate|計算|equation)\b',
            r'\b(homework|功課|essay|poem)\b',
            r'write.*(code|program|script|essay|story|poem)',
            r'help.*(code|program|script)',
        ]

        for pattern in irrelevant_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False

        # Check for person names (2+ words that look like names, case-insensitive)
        # This allows searching for contacts like "Stephen Wong" or "stephen wong"
        if re.match(r'^[A-Za-z]+\s+[A-Za-z]+$', query.strip()):
            return True  # Looks like a person name
        if re.match(r'^[\u4e00-\u9fff]{2,4}$', query.strip()):
            return True  # Looks like a Chinese name

        # Relevant keywords for a real estate company
        relevant_patterns = [
            # Property related
            r'物業|property|properties|listing|building|office|retail|shop|industrial|warehouse',
            r'cowork|共享|flexible|workspace',
            r'租|rent|lease|tenant|landlord',
            r'面積|sqft|呎|平方|area|size',
            r'地址|address|location|district|區',
            r'價|price|cost|budget',
            # CRM related
            r'客戶|customer|client|contact|lead|prospect',
            r'銷售|sales|deal|pipeline',
            r'業務|business|company',
            # Documents
            r'文件|document|contract|agreement|particular',
            # Company/work related
            r'c21|century\s*21|世紀',
            r'同事|colleague|staff|team|employee',
            r'會議|meeting|schedule|appointment',
            # General business queries
            r'佣金|commission',
            r'成交|transaction|deal',
            # Search actions
            r'find|search|look|show|查|找|搜',
            # Profile/info requests
            r'profile|info|detail|資料|檔案',
        ]

        for pattern in relevant_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True

        # Default: allow short queries (likely names or simple searches)
        # Only reject longer queries that don't match any pattern
        if len(query.strip()) <= 20:
            return True

        return False

    def _handle_irrelevant_query(self, query, start_time):
        """Handle queries that are not relevant to C21 business"""
        response = """抱歉，我只能回答與 C21 業務相關的問題，包括：

• **物業搜尋** - 寫字樓、商舖、工廈、共享空間
• **客戶查詢** - CRM 客戶、潛在客戶、聯絡人
• **物業文件** - 物業資料、合約文件

請問有什麼與物業或客戶相關的問題我可以幫到你？"""

        return {
            'response': response,
            'intent': 'rejected',
            'search_results': [],
            'sources': [],
            'model': None,
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
