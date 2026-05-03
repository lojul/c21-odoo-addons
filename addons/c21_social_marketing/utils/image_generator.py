# -*- coding: utf-8 -*-
"""
PIL-based image generator for C21 branded social media posts.
Generates images matching the C21 brand guidelines.
"""
import base64
import io
import logging
import requests
import os

_logger = logging.getLogger(__name__)

# Color palette
COLORS = {
    'navy_blue': '#1a365d',
    'sage_green': '#718a6e',
    'charcoal': '#374151',
    'terracotta': '#c67b5c',
    'gold': '#c9a962',
    'white': '#ffffff',
}

# Image dimensions (4:5 portrait for Instagram)
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350

# Margins (more space from edges)
MARGIN_HORIZONTAL = 100
MARGIN_VERTICAL = 80


def generate_post_image(headline, data_point='', background_color='navy_blue'):
    """
    Generate a branded C21 social media post image.

    Args:
        headline: Main headline text (Chinese)
        data_point: Secondary data point text (will be combined with headline)
        background_color: Color key from COLORS dict

    Returns:
        Base64 encoded PNG image
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        _logger.error("Pillow not installed. Run: pip install Pillow")
        raise ImportError("Pillow library required for image generation")

    # Get background color
    bg_color = COLORS.get(background_color, COLORS['navy_blue'])

    # Create base image
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_path = _get_font_path()
    try:
        font_main = ImageFont.truetype(font_path, 64)
        font_hashtags = ImageFont.truetype(font_path, 32)
    except Exception as e:
        _logger.warning(f"Could not load font {font_path}: {e}, using default")
        font_main = ImageFont.load_default()
        font_hashtags = font_main

    # Draw decorative lines (subtle gold geometric pattern)
    _draw_decorations(draw)

    # Combine headline and data_point as one sentence
    combined_text = headline or ''
    if data_point:
        # Add separator if headline doesn't end with punctuation
        if combined_text and not combined_text[-1] in '，。！？、：；':
            combined_text += '，'
        combined_text += data_point

    # Draw combined text (centered, wrapped) with more horizontal margin
    _draw_centered_text(
        draw, combined_text,
        font_main,
        y_position=IMAGE_HEIGHT * 0.45,
        max_width=IMAGE_WIDTH - (MARGIN_HORIZONTAL * 2),  # More space from edges
        color=COLORS['white']
    )

    # Draw hashtags (bottom left)
    hashtags = "#香港地產  #寫字樓  #商用樓  #地產新聞"
    draw.text(
        (MARGIN_HORIZONTAL, IMAGE_HEIGHT - 100),
        hashtags,
        font=font_hashtags,
        fill=COLORS['white']
    )

    # Draw C21 logo (bottom right) - use actual PNG logo
    _draw_c21_logo_png(img, IMAGE_WIDTH - MARGIN_HORIZONTAL - 80, IMAGE_HEIGHT - 160)

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def _get_font_path():
    """Get path to Chinese font"""
    # Try common font locations
    font_paths = [
        # Docker container (fonts-noto-cjk package)
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        # Debian/Ubuntu with fonts-noto-cjk
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        # Module's own font directory (fallback)
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoSansCJK-Bold.ttc'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoSansTC-Bold.ttf'),
        # System fonts - macOS (for local dev)
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
    ]

    for path in font_paths:
        if os.path.exists(path):
            return path

    _logger.warning("No Chinese font found, using default font")
    return None


def _draw_decorations(draw):
    """Draw subtle gold geometric lines"""
    gold = COLORS['gold']
    m = MARGIN_HORIZONTAL  # Use consistent margin

    # Top-left corner lines
    draw.line([(m, m), (m + 140, m)], fill=gold, width=2)
    draw.line([(m, m), (m, m + 140)], fill=gold, width=2)
    draw.line([(m + 40, m + 60), (m + 240, m + 60)], fill=gold, width=1)
    draw.line([(m + 60, m + 40), (m + 60, m + 190)], fill=gold, width=1)

    # Top-right corner
    draw.line([(IMAGE_WIDTH - m - 140, m + 20), (IMAGE_WIDTH - m, m + 20)], fill=gold, width=2)
    draw.line([(IMAGE_WIDTH - m - 20, m + 40), (IMAGE_WIDTH - m - 20, m + 140)], fill=gold, width=1)

    # Diagonal accents
    draw.line([(m + 20, m + 220), (m + 120, m + 120)], fill=gold, width=1)
    draw.line([(IMAGE_WIDTH - m - 90, m + 90), (IMAGE_WIDTH - m - 40, m + 140)], fill=gold, width=1)


def _draw_centered_text(draw, text, font, y_position, max_width, color):
    """Draw text centered and wrapped"""
    lines = _wrap_text(text, font, max_width, draw)

    # Calculate total height
    line_height = font.size + 20 if hasattr(font, 'size') else 80
    total_height = len(lines) * line_height
    start_y = y_position - (total_height / 2)

    for i, line in enumerate(lines):
        # Get text bounding box
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        x = (IMAGE_WIDTH - text_width) / 2
        y = start_y + (i * line_height)

        draw.text((x, y), line, font=font, fill=color)


def _wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width"""
    words = list(text)  # Split into characters for Chinese
    lines = []
    current_line = ""

    for char in words:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines


def _draw_c21_logo_png(img, x, y):
    """Draw C21 logo from PNG file"""
    from PIL import Image

    # Get logo path
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'c21_logo.png')

    try:
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert('RGBA')
            # Resize logo to fit (80x80 pixels)
            logo_size = 80
            logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

            # Calculate position (x, y is bottom-right corner)
            pos_x = x
            pos_y = y

            # Paste logo with transparency
            img.paste(logo, (pos_x, pos_y), logo)
        else:
            _logger.warning(f"C21 logo not found at {logo_path}")
    except Exception as e:
        _logger.warning(f"Failed to load C21 logo: {e}")


def upload_to_imgbb(api_key, image_base64):
    """
    Upload base64 image to imgbb and return public URL.

    Args:
        api_key: imgbb API key
        image_base64: Base64 encoded image data

    Returns:
        Public URL of uploaded image
    """
    if not api_key:
        raise ValueError("imgbb API key not configured")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key,
        'image': image_base64,
    }

    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    if data.get('success'):
        return data['data']['url']
    else:
        raise Exception(f"imgbb upload failed: {data.get('error', {}).get('message', 'Unknown error')}")
