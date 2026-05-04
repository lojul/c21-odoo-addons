# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # === LLM Provider Settings ===
    ai_assistant_provider = fields.Selection([
        ('openrouter', 'OpenRouter'),
        ('azure', 'Azure OpenAI'),
        ('ollama', 'Ollama (Local)'),
    ], string='AI Provider', default='openrouter',
        config_parameter='c21_ai_assistant.provider')

    ai_assistant_model = fields.Char(
        string='Model Name',
        config_parameter='c21_ai_assistant.model',
        default='meta-llama/llama-3.3-70b-instruct',
        help='Model identifier (e.g., meta-llama/llama-3.3-70b-instruct for OpenRouter)')

    ai_assistant_temperature = fields.Float(
        string='Temperature',
        config_parameter='c21_ai_assistant.temperature',
        default=0.7,
        help='Controls randomness (0.0 = deterministic, 1.0 = creative)')

    ai_assistant_max_tokens = fields.Integer(
        string='Max Tokens',
        config_parameter='c21_ai_assistant.max_tokens',
        default=2048,
        help='Maximum tokens in response')

    # === API Keys ===
    ai_assistant_openrouter_api_key = fields.Char(
        string='OpenRouter API Key (AI Assistant)',
        config_parameter='c21_ai_assistant.openrouter_api_key')

    ai_assistant_azure_endpoint = fields.Char(
        string='Azure OpenAI Endpoint',
        config_parameter='c21_ai_assistant.azure_endpoint',
        help='e.g., https://your-resource.openai.azure.com')

    ai_assistant_azure_api_key = fields.Char(
        string='Azure OpenAI API Key',
        config_parameter='c21_ai_assistant.azure_api_key')

    ai_assistant_azure_deployment = fields.Char(
        string='Azure Deployment Name',
        config_parameter='c21_ai_assistant.azure_deployment',
        default='gpt-4o')

    ai_assistant_ollama_url = fields.Char(
        string='Ollama URL',
        config_parameter='c21_ai_assistant.ollama_url',
        default='http://localhost:11434',
        help='Local Ollama server URL')

    # === n8n RAG Settings ===
    ai_assistant_rag_enabled = fields.Boolean(
        string='Enable Document Search (RAG)',
        config_parameter='c21_ai_assistant.rag_enabled',
        default=True)

    ai_assistant_rag_endpoint = fields.Char(
        string='n8n RAG Webhook URL',
        config_parameter='c21_ai_assistant.rag_endpoint',
        help='n8n webhook URL for document RAG')

    ai_assistant_rag_api_key = fields.Char(
        string='n8n RAG API Key',
        config_parameter='c21_ai_assistant.rag_api_key')

    # === Feature Toggles ===
    ai_assistant_property_search = fields.Boolean(
        string='Enable Property Search',
        config_parameter='c21_ai_assistant.property_search_enabled',
        default=True,
        help='Search c21.property.listing model')

    ai_assistant_crm_search = fields.Boolean(
        string='Enable CRM Search',
        config_parameter='c21_ai_assistant.crm_search_enabled',
        default=True,
        help='Search crm.lead and res.partner models')

    ai_assistant_general_qa = fields.Boolean(
        string='Enable General Q&A',
        config_parameter='c21_ai_assistant.general_qa_enabled',
        default=True,
        help='Allow general questions to be answered by LLM')

    # === System Prompt (Text fields need manual handling) ===
    ai_assistant_system_prompt = fields.Text(
        string='System Prompt',
        help='Custom system prompt for the AI assistant')

    ai_assistant_welcome_message = fields.Text(
        string='Welcome Message',
        default='Hello! I am the C21 AI Assistant. I can help you search properties, query CRM data, or answer general questions. How can I help you?')

    # === Advanced Settings ===
    ai_assistant_max_search_results = fields.Integer(
        string='Max Search Results',
        config_parameter='c21_ai_assistant.max_search_results',
        default=10,
        help='Maximum number of results to return from Odoo searches')

    ai_assistant_session_timeout = fields.Integer(
        string='Session Timeout (minutes)',
        config_parameter='c21_ai_assistant.session_timeout',
        default=30,
        help='Session timeout in minutes')

    ai_assistant_debug_mode = fields.Boolean(
        string='Debug Mode',
        config_parameter='c21_ai_assistant.debug_mode',
        default=False,
        help='Enable detailed logging for debugging')

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        # Manually load Text fields
        res['ai_assistant_system_prompt'] = ICP.get_param('c21_ai_assistant.system_prompt', default='')
        res['ai_assistant_welcome_message'] = ICP.get_param('c21_ai_assistant.welcome_message', default='Hello! I am the C21 AI Assistant. I can help you search properties, query CRM data, or answer general questions. How can I help you?')
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        # Manually save Text fields
        ICP.set_param('c21_ai_assistant.system_prompt', self.ai_assistant_system_prompt or '')
        ICP.set_param('c21_ai_assistant.welcome_message', self.ai_assistant_welcome_message or '')
