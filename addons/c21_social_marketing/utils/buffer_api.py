# -*- coding: utf-8 -*-
"""
Buffer API integration for social media posting.
Uses Buffer's GraphQL RPC endpoint.
"""
import json
import logging
import requests

_logger = logging.getLogger(__name__)

BUFFER_API_URL = "https://api.buffer.com/rpc"


def create_post(api_token, channel_id, text, image_url=None, platform='instagram'):
    """
    Create a post in Buffer (scheduled for next available slot).

    Args:
        api_token: Buffer API token
        channel_id: Buffer channel ID
        text: Post text/caption
        image_url: Optional public image URL
        platform: Platform type (instagram, facebook, threads)

    Returns:
        Dict with post ID and status
    """
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }

    # Build GraphQL mutation
    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            __typename
            ... on PostActionSuccess {
                post {
                    id
                    status
                }
            }
            ... on UnexpectedError {
                message
            }
        }
    }
    """

    # Build input based on platform
    post_input = {
        'channelId': channel_id,
        'schedulingType': 'automatic',  # Next available slot
        'mode': 'addToQueue',  # Required by Buffer API
        'text': text,
    }

    # Add image if provided
    if image_url:
        post_input['assets'] = {
            'images': [{'url': image_url}]
        }

    # Platform-specific metadata
    if platform == 'instagram':
        post_input['metadata'] = {
            'instagram': {
                'type': 'post',
                'shouldShareToFeed': True
            }
        }
    elif platform == 'facebook':
        post_input['metadata'] = {
            'facebook': {
                'type': 'post'
            }
        }
    elif platform == 'threads':
        post_input['metadata'] = {
            'threads': {}
        }

    payload = {
        'query': mutation,
        'variables': {
            'input': post_input
        }
    }

    _logger.info(f"Creating Buffer post for channel {channel_id} ({platform})")

    response = requests.post(
        BUFFER_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()

    # Check for errors
    if 'errors' in data:
        error_msg = data['errors'][0].get('message', 'Unknown error')
        raise Exception(f"Buffer API error: {error_msg}")

    create_post_result = data.get('data', {}).get('createPost', {})

    if create_post_result.get('__typename') == 'UnexpectedError':
        raise Exception(f"Buffer error: {create_post_result.get('message')}")

    post_data = create_post_result.get('post', {})

    return {
        'success': True,
        'post_id': post_data.get('id'),
        'status': post_data.get('status'),
    }


def get_channels(api_token):
    """
    Get list of connected channels from Buffer.

    Args:
        api_token: Buffer API token

    Returns:
        List of channel dicts
    """
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }

    query = """
    query GetChannels {
        channels {
            id
            name
            service
            avatar
        }
    }
    """

    response = requests.post(
        BUFFER_API_URL,
        headers=headers,
        json={'query': query},
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    return data.get('data', {}).get('channels', [])


def test_connection(api_token):
    """Test Buffer API connection by fetching channels"""
    try:
        channels = get_channels(api_token)
        channel_names = [c.get('name', 'Unknown') for c in channels[:3]]
        return f"Found {len(channels)} channels: {', '.join(channel_names)}"
    except Exception as e:
        raise Exception(f"Buffer connection failed: {str(e)}")
