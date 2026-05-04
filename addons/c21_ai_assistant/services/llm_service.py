# -*- coding: utf-8 -*-

import requests
import json
import logging
import time
from datetime import datetime

_logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM providers"""

    def __init__(self, env):
        self.env = env
        self._load_config()

    def _load_config(self):
        """Load configuration from ir.config_parameter"""
        ICP = self.env['ir.config_parameter'].sudo()

        self.provider = ICP.get_param('c21_ai_assistant.provider', 'openrouter')
        self.model = ICP.get_param('c21_ai_assistant.model', 'meta-llama/llama-3.3-70b-instruct')
        self.temperature = float(ICP.get_param('c21_ai_assistant.temperature', '0.7'))
        self.max_tokens = int(ICP.get_param('c21_ai_assistant.max_tokens', '2048'))
        self.debug_mode = ICP.get_param('c21_ai_assistant.debug_mode', 'False') == 'True'

        # Provider-specific settings
        self.openrouter_api_key = ICP.get_param('c21_ai_assistant.openrouter_api_key', '')
        self.azure_endpoint = ICP.get_param('c21_ai_assistant.azure_endpoint', '')
        self.azure_api_key = ICP.get_param('c21_ai_assistant.azure_api_key', '')
        self.azure_deployment = ICP.get_param('c21_ai_assistant.azure_deployment', 'gpt-4o')
        self.ollama_url = ICP.get_param('c21_ai_assistant.ollama_url', 'http://localhost:11434')

        # System prompt
        self.system_prompt = ICP.get_param('c21_ai_assistant.system_prompt', '')

    def _get_formatted_system_prompt(self):
        """Format system prompt with dynamic variables"""
        prompt = self.system_prompt or self._get_default_system_prompt()
        return prompt.format(
            current_date=datetime.now().strftime('%Y-%m-%d'),
            user_name=self.env.user.name,
            company_name=self.env.company.name
        )

    def _get_default_system_prompt(self):
        return """You are C21Net AI Assistant, a helpful assistant for a commercial real estate company in Hong Kong.

Your capabilities:
1. Search property listings (offices, retail, industrial spaces, coworking)
2. Query CRM leads and contacts
3. Search property documents and particulars
4. Answer general questions about real estate

Guidelines:
- Respond in the same language as the user (English or Chinese)
- When showing property results, include key details: name, address, area, rent
- For CRM queries, respect user access permissions
- Cite document sources when using RAG results
- Be concise but helpful
- If you cannot find information, say so clearly

Current date: {current_date}
User: {user_name}
Company: {company_name}"""

    def chat(self, messages, context=None):
        """
        Send chat request to LLM

        Args:
            messages: List of message dicts with 'role' and 'content'
            context: Optional additional context to include

        Returns:
            dict with 'content', 'tokens_used', 'model', 'response_time'
        """
        start_time = time.time()

        # Build messages with system prompt
        full_messages = [
            {'role': 'system', 'content': self._get_formatted_system_prompt()}
        ]

        # Add context if provided
        if context:
            full_messages.append({
                'role': 'system',
                'content': f"Additional context:\n{context}"
            })

        # Add conversation history
        full_messages.extend(messages)

        if self.debug_mode:
            _logger.info(f"[AI Assistant] Sending to {self.provider}: {len(full_messages)} messages")

        try:
            if self.provider == 'openrouter':
                result = self._call_openrouter(full_messages)
            elif self.provider == 'azure':
                result = self._call_azure(full_messages)
            elif self.provider == 'ollama':
                result = self._call_ollama(full_messages)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            result['response_time'] = time.time() - start_time

            if self.debug_mode:
                _logger.info(f"[AI Assistant] Response received in {result['response_time']:.2f}s, "
                           f"tokens: {result.get('tokens_used', 'N/A')}")

            return result

        except Exception as e:
            _logger.error(f"[AI Assistant] LLM error: {str(e)}")
            return {
                'content': f"抱歉，AI 服務暫時無法使用。錯誤: {str(e)}",
                'tokens_used': 0,
                'model': self.model,
                'response_time': time.time() - start_time,
                'error': str(e)
            }

    def _call_openrouter(self, messages):
        """Call OpenRouter API"""
        if not self.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured")

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://c21net.com",
            "X-Title": "C21 AI Assistant"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return {
            'content': data['choices'][0]['message']['content'],
            'tokens_used': data.get('usage', {}).get('total_tokens', 0),
            'model': data.get('model', self.model),
        }

    def _call_azure(self, messages):
        """Call Azure OpenAI API"""
        if not self.azure_endpoint or not self.azure_api_key:
            raise ValueError("Azure OpenAI endpoint or API key not configured")

        url = f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}/chat/completions?api-version=2024-02-01"
        headers = {
            "api-key": self.azure_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return {
            'content': data['choices'][0]['message']['content'],
            'tokens_used': data.get('usage', {}).get('total_tokens', 0),
            'model': self.azure_deployment,
        }

    def _call_ollama(self, messages):
        """Call local Ollama API"""
        url = f"{self.ollama_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            }
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        return {
            'content': data['message']['content'],
            'tokens_used': data.get('eval_count', 0) + data.get('prompt_eval_count', 0),
            'model': self.model,
        }

    def analyze_query(self, query, conversation_history=None):
        """
        Use LLM to intelligently analyze a user query and extract:
        - Intent (property_search, crm_search, document_search, greeting, general, rejected)
        - Search parameters (for property: location, property_type, rent_range, area_range, etc.)
        - Search term (the actual thing to search for)

        Returns:
            dict with 'intent', 'search_term', 'filters', 'is_followup'
        """
        # Build context from conversation history
        history_context = ""
        if conversation_history:
            recent = conversation_history[-4:]  # Last 2 exchanges
            history_context = "\n".join([
                f"{msg['role'].upper()}: {msg['content'][:200]}"
                for msg in recent
            ])

        analysis_prompt = f"""Analyze this user query for a Hong Kong commercial real estate assistant.

CONVERSATION HISTORY:
{history_context if history_context else "(No previous messages)"}

CURRENT QUERY: "{query}"

Determine:
1. intent: One of:
   - "property_search" - looking for properties, buildings, offices, shops, locations
   - "crm_search" - looking for people, contacts, customers, leads
   - "document_search" - looking for documents, files, PDFs, particulars
   - "greeting" - hello, hi, help
   - "rejected" - off-topic (coding, recipes, games, etc.)
   - "general" - other business-related questions

2. search_term: The main thing to search for (location name, person name, building name, etc.)

3. filters: Extract any specific criteria mentioned:
   - district: location/area (e.g., "中環", "Ma On Shan", "銅鑼灣")
   - property_type: office/retail/industrial/coworking
   - min_rent / max_rent: monthly rent in HKD
   - min_area / max_area: area in sqft
   - building_name: specific building mentioned

4. is_followup: true if referring to previous results ("his profile", "open it", "the first one")

5. model_type: for crm_search, specify "partner" for contacts or "lead" for sales leads

Respond ONLY with valid JSON, no explanation:
{{"intent": "...", "search_term": "...", "filters": {{}}, "is_followup": false, "model_type": "partner"}}"""

        messages = [
            {'role': 'system', 'content': 'You are a query analyzer. Return only valid JSON.'},
            {'role': 'user', 'content': analysis_prompt}
        ]

        try:
            result = self.chat(messages)
            content = result.get('content', '{}')

            # Extract JSON from response (handle markdown code blocks)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            parsed = json.loads(content.strip())

            if self.debug_mode:
                _logger.info(f"[AI Assistant] Query analysis: {parsed}")

            return {
                'intent': parsed.get('intent', 'general'),
                'search_term': parsed.get('search_term', query),
                'filters': parsed.get('filters', {}),
                'is_followup': parsed.get('is_followup', False),
                'model_type': parsed.get('model_type', 'partner'),
                'tokens_used': result.get('tokens_used', 0),
            }

        except (json.JSONDecodeError, Exception) as e:
            _logger.warning(f"[AI Assistant] Query analysis failed: {e}, falling back to simple detection")
            # Fallback to simple detection
            return {
                'intent': 'general',
                'search_term': query,
                'filters': {},
                'is_followup': False,
                'model_type': 'partner',
                'tokens_used': 0,
            }
