# -*- coding: utf-8 -*-
"""
RSS feed scraper for property news.
"""
import logging
import re
import requests
from datetime import datetime, timedelta
from xml.etree import ElementTree

_logger = logging.getLogger(__name__)

# Keywords for property news filtering
PROPERTY_KEYWORDS = [
    # Chinese
    '地產', '樓市', '物業', '寫字樓', '商廈', '工廈', '租金', '呎租',
    '成交', '甲級', '商業', '辦公', '置業', '投資', '收購', '出售',
    '空置', '吸納', '商場', '零售', '工業', '倉庫', '舖位', '業主',
    '租客', '業權', '按揭', '估值', '樓價', '租務', '物管',
    # English
    'property', 'office', 'commercial', 'lease', 'rent', 'real estate',
    'retail', 'industrial', 'warehouse', 'vacancy', 'transaction',
]


def fetch_feed(env, feed, max_items=50, max_age_days=30):
    """
    Fetch and parse RSS feed, create news records.

    Args:
        env: Odoo environment
        feed: c21.social.feed record
        max_items: Maximum items to fetch per feed (default 50)
        max_age_days: Only fetch items published within this many days (default 7)
    """
    _logger.info(f"Fetching RSS feed: {feed.name} ({feed.url})")

    try:
        response = requests.get(feed.url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; C21Bot/1.0)'
        })
        response.raise_for_status()
        content = response.text
    except Exception as e:
        _logger.error(f"Failed to fetch feed {feed.name}: {e}")
        return

    # Parse RSS/XML
    items = _parse_rss(content)
    _logger.info(f"Found {len(items)} items in feed {feed.name}")

    # Filter by date - only keep recent items
    now = datetime.now()
    cutoff_date = now - timedelta(days=max_age_days)
    filtered_items = []
    skipped_future = 0
    skipped_old = 0

    for item in items:
        pub_date = item.get('pub_date')
        if pub_date:
            # Skip items with future dates (likely parsing errors)
            if pub_date > now:
                _logger.warning(f"Skipping future date: {item['title'][:50]} ({pub_date})")
                skipped_future += 1
                continue
            # Skip items older than max_age_days
            if pub_date < cutoff_date:
                skipped_old += 1
                continue
        filtered_items.append(item)

    _logger.info(f"Date filter: {len(filtered_items)} recent, {skipped_old} old, {skipped_future} future")

    # Limit items
    filtered_items = filtered_items[:max_items]

    # Create news records
    news_model = env['c21.social.news']
    created_count = 0
    duplicate_count = 0

    for item in filtered_items:
        # Check if already exists
        existing = news_model.search([('url', '=', item['url'])], limit=1)
        if existing:
            duplicate_count += 1
            continue

        # Check relevance
        is_property, score = _check_relevance(item['title'], item['description'])

        news_model.create({
            'name': item['title'][:500],
            'description': item['description'][:2000] if item['description'] else '',
            'url': item['url'],
            'source': feed.name,
            'feed_id': feed.id,
            'publish_date': item.get('pub_date'),
            'is_property_news': is_property,
            'relevance_score': score,
        })
        created_count += 1

    # Update feed last fetch time
    feed.last_fetch = datetime.now()

    _logger.info(f"Feed {feed.name}: {created_count} new, {duplicate_count} duplicates")


def _parse_rss(content):
    """Parse RSS XML content and extract items"""
    items = []

    try:
        # Handle CDATA and namespaces
        content = content.replace('xmlns=', 'xmlns_ignore=')
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as e:
        _logger.error(f"XML parse error: {e}")
        return items

    # Find items (RSS 2.0 or Atom)
    for item in root.findall('.//item'):
        title = _get_text(item, 'title')
        link = _get_text(item, 'link')
        description = _get_text(item, 'description')
        pub_date = _parse_date(_get_text(item, 'pubDate'))

        if title and link:
            items.append({
                'title': _clean_text(title),
                'url': link,
                'description': _clean_text(description),
                'pub_date': pub_date,
            })

    # Also try Atom format
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = _get_text(entry, '{http://www.w3.org/2005/Atom}title')
        link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
        link = link_elem.get('href') if link_elem is not None else ''
        summary = _get_text(entry, '{http://www.w3.org/2005/Atom}summary')
        published = _parse_date(_get_text(entry, '{http://www.w3.org/2005/Atom}published'))

        if title and link:
            items.append({
                'title': _clean_text(title),
                'url': link,
                'description': _clean_text(summary),
                'pub_date': published,
            })

    return items


def _get_text(element, tag):
    """Get text content from XML element"""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return ''


def _clean_text(text):
    """Clean HTML and special characters from text"""
    if not text:
        return ''

    # Remove CDATA markers
    text = re.sub(r'<!\[CDATA\[|\]\]>', '', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode common entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')

    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def _parse_date(date_str):
    """Parse RSS date string to datetime (returns naive UTC datetime for Odoo)"""
    if not date_str:
        return None

    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            # Convert to naive datetime (Odoo requirement)
            if dt.tzinfo is not None:
                # Convert to UTC and remove timezone info
                from datetime import timezone
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except ValueError:
            continue

    return None


def _check_relevance(title, description):
    """
    Check if news is property-related and calculate relevance score.

    Returns:
        (is_property_news: bool, score: int)
    """
    text = f"{title} {description or ''}".lower()
    score = 0

    for keyword in PROPERTY_KEYWORDS:
        if keyword.lower() in text:
            score += 10

    # Boost for specific high-value terms
    high_value = ['甲級寫字樓', '商業地產', '租金', '呎租', '成交', 'grade a']
    for term in high_value:
        if term.lower() in text:
            score += 20

    is_property = score >= 10
    return is_property, score


def fetch_all_feeds(env, cleanup=True):
    """Fetch all active feeds and optionally cleanup old news"""
    feeds = env['c21.social.feed'].search([('active', '=', True)])
    for feed in feeds:
        try:
            fetch_feed(env, feed)
        except Exception as e:
            _logger.exception(f"Error fetching feed {feed.name}")

    # Cleanup old and invalid news after fetching
    if cleanup:
        news_model = env['c21.social.news']
        deleted = news_model.cleanup_old_news(days=14)
        invalid = news_model.cleanup_invalid_news()
        _logger.info(f"Cleanup: removed {deleted} old news, {invalid} invalid news")
