# -*- coding: utf-8 -*-
"""
AI caption generator using OpenRouter (DeepSeek, etc.)
"""
import json
import logging
import requests

_logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """你是香港商業地產市場分析師，為世紀21(Century 21)地產公司撰寫社交媒體帖文。

從以下新聞中選出最重要的一則商業地產新聞。必須包含具體數據（數字、地區名、大廈名或成交價）。

只輸出JSON格式（不要markdown代碼塊）：
{
  "headline_zh": "15-20字繁體中文標題，完整描述新聞重點",
  "data_point": "10-15字關鍵數據（如：淨吸納21.7萬呎、租金升2.4%、成交價22億）",
  "district": "涉及地區",
  "ig_caption": "Instagram說明文（1句，100字內，專業簡潔）",
  "fb_caption": "Facebook說明文（2-3句，200字內，解釋數據意義）",
  "threads_caption": "Threads說明文（1-2句對話式，可加提問引發討論）",
  "source": "新聞來源及日期",
  "background_color": "navy_blue（預設）| sage_green（正面/復甦）| charcoal（謹慎/下跌）| terracotta（重大交易）"
}

重要：headline_zh 和 data_point 組合起來應有25-35字，用於圖片顯示。
語調：專業、數據導向。不用感嘆號、不用emoji。"""


def generate_captions(api_key, news_content, model='deepseek/deepseek-chat', temperature=0.5):
    """
    Generate social media captions from news content.

    Args:
        api_key: OpenRouter API key
        news_content: News text to summarize
        model: OpenRouter model ID
        temperature: AI temperature (0-1)

    Returns:
        Dict with headline_zh, data_point, captions, etc.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://c21net.com',
        'X-Title': 'C21 Social Marketing',
    }

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': f'今日新聞：\n{news_content}'}
        ],
        'temperature': temperature,
        'max_tokens': 1000,
    }

    _logger.info(f"Calling OpenRouter API with model {model}")

    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()

    data = response.json()
    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

    # Parse JSON from response
    return _parse_json_response(content)


def _parse_json_response(content):
    """Parse JSON from AI response, handling markdown code blocks"""
    # Remove markdown code blocks if present
    content = content.strip()
    if content.startswith('```json'):
        content = content[7:]
    if content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        _logger.error(f"Failed to parse AI response as JSON: {e}")
        _logger.debug(f"Raw content: {content[:500]}")

        # Return fallback
        return {
            'headline_zh': '香港商業地產市場動態',
            'data_point': '最新市場資訊',
            'district': '香港',
            'ig_caption': '香港商業地產最新動態',
            'fb_caption': '了解香港商業地產市場的最新發展。',
            'threads_caption': '今日香港商業地產市場有新動態，你點睇？',
            'source': '綜合報導',
            'background_color': 'navy_blue',
            'parse_error': str(e),
            'raw_content': content[:500],
        }


def test_connection(api_key):
    """Test OpenRouter API connection"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': 'deepseek/deepseek-chat',
        'messages': [
            {'role': 'user', 'content': 'Say "OK" only.'}
        ],
        'max_tokens': 10,
    }

    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    model = data.get('model', 'unknown')
    return f"Model: {model}"
