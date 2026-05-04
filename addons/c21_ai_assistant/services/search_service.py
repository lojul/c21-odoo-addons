# -*- coding: utf-8 -*-

import logging
import re

_logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching Odoo models"""

    def __init__(self, env):
        self.env = env
        self._load_config()

    def _load_config(self):
        """Load configuration from ir.config_parameter"""
        ICP = self.env['ir.config_parameter'].sudo()

        self.property_search_enabled = ICP.get_param(
            'c21_ai_assistant.property_search_enabled', 'True') == 'True'
        self.crm_search_enabled = ICP.get_param(
            'c21_ai_assistant.crm_search_enabled', 'True') == 'True'
        self.max_results = int(ICP.get_param(
            'c21_ai_assistant.max_search_results', '10'))
        self.debug_mode = ICP.get_param(
            'c21_ai_assistant.debug_mode', 'False') == 'True'

    def search_properties(self, query, filters=None):
        """
        Search property listings

        Args:
            query: Search query string
            filters: Optional dict of filters (district, property_type, etc.)

        Returns:
            dict with 'results', 'count', 'formatted'
        """
        if not self.property_search_enabled:
            return {'error': 'Property search is disabled', 'results': [], 'count': 0}

        # Check if the model exists
        if 'c21.property.listing' not in self.env:
            return {'error': 'Property listing module not installed', 'results': [], 'count': 0}

        try:
            PropertyListing = self.env['c21.property.listing']

            # Build domain from query and filters
            domain = self._build_property_domain(query, filters)

            if self.debug_mode:
                _logger.info(f"[AI Assistant] Property search domain: {domain}")

            # Search with limit
            properties = PropertyListing.search(domain, limit=self.max_results)

            results = []
            for prop in properties:
                results.append({
                    'id': prop.id,
                    'ref_code': prop.ref_code or '',
                    'name': prop.name or '',
                    'name_cn': getattr(prop, 'name_cn', '') or '',
                    'building_name': getattr(prop, 'building_name', '') or '',
                    'address': self._format_property_address(prop),
                    'district': getattr(prop, 'district', '') or '',
                    'property_type': getattr(prop, 'property_type_id', False) and prop.property_type_id.name or '',
                    'gross_area': getattr(prop, 'gross_area', 0) or 0,
                    'net_area': getattr(prop, 'net_area', 0) or 0,
                    'asking_rent': getattr(prop, 'asking_rent', 0) or 0,
                    'rent_per_sqft': getattr(prop, 'rent_per_sqft', 0) or 0,
                    'publish_status': getattr(prop, 'publish_status', '') or '',
                })

            return {
                'results': results,
                'count': len(results),
                'total': PropertyListing.search_count(domain),
                'formatted': self._format_property_results(results),
            }

        except Exception as e:
            _logger.error(f"[AI Assistant] Property search error: {str(e)}")
            return {'error': str(e), 'results': [], 'count': 0}

    def _build_property_domain(self, query, filters=None):
        """Build search domain for properties"""
        domain = []

        # Text search across multiple fields including district
        if query:
            query_lower = query.lower()
            domain.append('|')
            domain.append('|')
            domain.append('|')
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', query))
            domain.append(('name_cn', 'ilike', query))
            domain.append(('building_name', 'ilike', query))
            domain.append(('address', 'ilike', query))
            domain.append(('district', 'ilike', query))
            domain.append(('ref_code', 'ilike', query))

        # Apply filters
        if filters:
            if filters.get('district'):
                domain.append(('district', 'ilike', filters['district']))
            if filters.get('property_type'):
                domain.append(('property_type_id.name', 'ilike', filters['property_type']))
            if filters.get('min_area'):
                domain.append(('gross_area', '>=', filters['min_area']))
            if filters.get('max_area'):
                domain.append(('gross_area', '<=', filters['max_area']))
            if filters.get('min_rent'):
                domain.append(('asking_rent', '>=', filters['min_rent']))
            if filters.get('max_rent'):
                domain.append(('asking_rent', '<=', filters['max_rent']))
            if filters.get('publish_status'):
                domain.append(('publish_status', '=', filters['publish_status']))

        return domain

    def _format_property_address(self, prop):
        """Format property address from components"""
        parts = []
        if hasattr(prop, 'floor') and prop.floor:
            parts.append(prop.floor)
        if hasattr(prop, 'unit') and prop.unit:
            parts.append(prop.unit)
        if hasattr(prop, 'building_name') and prop.building_name:
            parts.append(prop.building_name)
        if hasattr(prop, 'address') and prop.address:
            parts.append(prop.address)
        return ', '.join(filter(None, parts))

    def _format_property_results(self, results):
        """Format property results for display with clickable links"""
        if not results:
            return "未找到符合條件的物業。"

        lines = [f"找到 {len(results)} 個物業:\n"]
        for i, prop in enumerate(results[:5], 1):
            record_id = prop.get('id')
            name = prop.get('name_cn') or prop.get('name') or '未命名'
            address = prop.get('address') or ''
            area = prop.get('gross_area') or 0
            rent = prop.get('asking_rent') or 0

            # Make name a clickable link to the property form
            link = f"/web#id={record_id}&model=c21.property.listing&view_type=form"
            line = f"{i}. **[{name}]({link})**"
            if address:
                line += f"\n   地址: {address}"
            if area:
                line += f"\n   面積: {area:,.0f} 呎"
            if rent:
                line += f"\n   租金: HK${rent:,.0f}/月"
            lines.append(line)

        if len(results) > 5:
            lines.append(f"\n... 還有 {len(results) - 5} 個結果")

        return "\n".join(lines)

    def search_crm(self, query, model_type='lead', filters=None):
        """
        Search CRM leads or contacts

        Args:
            query: Search query string
            model_type: 'lead' or 'partner'
            filters: Optional dict of filters

        Returns:
            dict with 'results', 'count', 'formatted'
        """
        if not self.crm_search_enabled:
            return {'error': 'CRM search is disabled', 'results': [], 'count': 0}

        try:
            if model_type == 'lead':
                return self._search_leads(query, filters)
            elif model_type == 'partner':
                return self._search_partners(query, filters)
            else:
                return {'error': f'Unknown model type: {model_type}', 'results': [], 'count': 0}

        except Exception as e:
            _logger.error(f"[AI Assistant] CRM search error: {str(e)}")
            return {'error': str(e), 'results': [], 'count': 0}

    def _search_leads(self, query, filters=None):
        """Search CRM leads"""
        if 'crm.lead' not in self.env:
            return {'error': 'CRM module not installed', 'results': [], 'count': 0}

        Lead = self.env['crm.lead']

        domain = []
        if query:
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', query))
            domain.append(('partner_id.name', 'ilike', query))
            domain.append(('email_from', 'ilike', query))

        if filters:
            if filters.get('stage'):
                domain.append(('stage_id.name', 'ilike', filters['stage']))
            if filters.get('user_id'):
                domain.append(('user_id', '=', filters['user_id']))

        leads = Lead.search(domain, limit=self.max_results)

        results = []
        for lead in leads:
            results.append({
                'id': lead.id,
                'name': lead.name or '',
                'partner_name': lead.partner_id.name if lead.partner_id else '',
                'email': lead.email_from or '',
                'phone': lead.phone or '',
                'stage': lead.stage_id.name if lead.stage_id else '',
                'expected_revenue': lead.expected_revenue or 0,
                'user': lead.user_id.name if lead.user_id else '',
                'create_date': lead.create_date.strftime('%Y-%m-%d') if lead.create_date else '',
            })

        return {
            'results': results,
            'count': len(results),
            'total': Lead.search_count(domain),
            'formatted': self._format_lead_results(results),
        }

    def _format_lead_results(self, results):
        """Format lead results for display with clickable links"""
        if not results:
            return "未找到符合條件的潛在客戶。"

        lines = [f"找到 {len(results)} 個潛在客戶:\n"]
        for i, lead in enumerate(results[:5], 1):
            record_id = lead.get('id')
            name = lead.get('name', '未命名')
            # Make name a clickable link to the lead form
            link = f"/web#id={record_id}&model=crm.lead&view_type=form"
            line = f"{i}. **[{name}]({link})**"
            if lead.get('partner_name'):
                line += f" - {lead['partner_name']}"
            if lead.get('stage'):
                line += f"\n   階段: {lead['stage']}"
            if lead.get('email'):
                line += f"\n   電郵: {lead['email']}"
            if lead.get('expected_revenue'):
                line += f"\n   預期收入: HK${lead['expected_revenue']:,.0f}"
            lines.append(line)

        if len(results) > 5:
            lines.append(f"\n... 還有 {len(results) - 5} 個結果")

        return "\n".join(lines)

    def _search_partners(self, query, filters=None):
        """Search contacts/partners"""
        Partner = self.env['res.partner']

        domain = [('is_company', '=', False)]  # Search individuals by default
        if query:
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', query))
            domain.append(('email', 'ilike', query))
            domain.append(('phone', 'ilike', query))

        if filters:
            if filters.get('is_company') is not None:
                domain = [d for d in domain if d != ('is_company', '=', False)]
                domain.append(('is_company', '=', filters['is_company']))
            if filters.get('customer_rank'):
                domain.append(('customer_rank', '>', 0))

        partners = Partner.search(domain, limit=self.max_results)

        results = []
        for partner in partners:
            results.append({
                'id': partner.id,
                'name': partner.name or '',
                'email': partner.email or '',
                'phone': partner.phone or partner.mobile or '',
                'company': partner.parent_id.name if partner.parent_id else '',
                'city': partner.city or '',
                'is_company': partner.is_company,
            })

        return {
            'results': results,
            'count': len(results),
            'total': Partner.search_count(domain),
            'formatted': self._format_partner_results(results),
        }

    def _format_partner_results(self, results):
        """Format partner results for display with clickable links"""
        if not results:
            return "未找到符合條件的聯絡人。"

        lines = [f"找到 {len(results)} 個聯絡人:\n"]
        for i, partner in enumerate(results[:5], 1):
            record_id = partner.get('id')
            name = partner.get('name', '未命名')
            # Make name a clickable link to the contact form
            link = f"/web#id={record_id}&model=res.partner&view_type=form"
            line = f"{i}. **[{name}]({link})**"
            if partner.get('company'):
                line += f" ({partner['company']})"
            if partner.get('email'):
                line += f"\n   電郵: {partner['email']}"
            if partner.get('phone'):
                line += f"\n   電話: [{partner['phone']}]({link})"
            lines.append(line)

        if len(results) > 5:
            lines.append(f"\n... 還有 {len(results) - 5} 個結果")

        return "\n".join(lines)

    def extract_search_params(self, query):
        """
        Extract search parameters from natural language query

        Returns dict with:
            - search_term: Main search text
            - filters: Extracted filter values
        """
        filters = {}
        search_term = query

        # Extract area patterns (e.g., "2000 sqft", "2000呎")
        area_match = re.search(r'(\d+(?:,\d+)?)\s*(?:sqft|呎|平方呎|sq\.?ft)', query, re.IGNORECASE)
        if area_match:
            area_value = int(area_match.group(1).replace(',', ''))
            # Check if it's minimum or maximum
            if '以上' in query or 'above' in query.lower() or 'over' in query.lower():
                filters['min_area'] = area_value
            elif '以下' in query or 'under' in query.lower() or 'below' in query.lower():
                filters['max_area'] = area_value
            else:
                filters['min_area'] = area_value  # Default to minimum

        # Extract rent patterns (e.g., "$50000", "5萬", "20k-30k")
        # First try range pattern: "20k-30k" or "20000-30000"
        rent_range_match = re.search(r'(\d+)\s*k?\s*[-~到]\s*(\d+)\s*k?', query, re.IGNORECASE)
        if rent_range_match:
            min_val = int(rent_range_match.group(1))
            max_val = int(rent_range_match.group(2))
            # Check if using 'k' notation
            if 'k' in query.lower():
                min_val *= 1000
                max_val *= 1000
            filters['min_rent'] = min_val
            filters['max_rent'] = max_val
        else:
            # Single value pattern (e.g., "$50000", "5萬")
            rent_match = re.search(r'\$?(\d+(?:,\d+)?)\s*(?:萬|万|k)?(?:/月|per month)?', query, re.IGNORECASE)
            if rent_match:
                rent_value = int(rent_match.group(1).replace(',', ''))
                if '萬' in query or '万' in query:
                    rent_value *= 10000
                elif 'k' in query.lower():
                    rent_value *= 1000
                filters['max_rent'] = rent_value

        # Extract district patterns
        districts = ['中環', 'Central', '金鐘', 'Admiralty', '灣仔', 'Wan Chai',
                    '銅鑼灣', 'Causeway Bay', '北角', 'North Point', '鰂魚涌', 'Quarry Bay',
                    '尖沙咀', 'Tsim Sha Tsui', '旺角', 'Mong Kok', '觀塘', 'Kwun Tong',
                    '荃灣', 'Tsuen Wan', '沙田', 'Sha Tin', '上環', 'Sheung Wan']
        for district in districts:
            if district.lower() in query.lower():
                filters['district'] = district
                break

        # Extract property type patterns
        property_types = {
            '寫字樓': 'Office', 'office': 'Office', '辦公室': 'Office',
            '零售': 'Retail', 'retail': 'Retail', '商舖': 'Retail', 'shop': 'Retail',
            '工業': 'Industrial', 'industrial': 'Industrial', '廠房': 'Industrial',
            'coworking': 'Coworking', '共享空間': 'Coworking',
        }
        for pattern, prop_type in property_types.items():
            if pattern.lower() in query.lower():
                filters['property_type'] = prop_type
                break

        return {
            'search_term': search_term,
            'filters': filters,
        }
