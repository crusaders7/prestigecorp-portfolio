#!/usr/bin/env python3
"""
Google CSE News Search API - Vercel Serverless Function
Simple function format for Vercel deployment
"""
import json
import os
from datetime import datetime

# Try to import Google CSE modules
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from protected_cse import ProtectedGoogleCSE
    PROTECTION_AVAILABLE = True
except ImportError:
    PROTECTION_AVAILABLE = False

def handler(request):
    """Vercel serverless function handler"""
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Method not allowed. Use POST.',
                'method': request.method
            })
        }

    try:
        # Parse request body
        if hasattr(request, 'body') and request.body:
            data = json.loads(request.body)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'No request body'})
            }

        # Extract search parameters
        query = data.get('query', '').strip()
        sources = data.get('sources', [])
        max_results = data.get('max_results', 10)

        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Query parameter is required'})
            }

        # Perform search
        search_results = search_news(query, sources, max_results)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(search_results, ensure_ascii=False)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        }

def search_news(query, sources, max_results):
    """Search for news using Google Custom Search Engine"""

    # Check if Google CSE is available
    if not GOOGLE_AVAILABLE:
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': 'Google API client not available',
            'timestamp': datetime.now().isoformat()
        }

    # Get API credentials from environment
    api_key = os.environ.get('GOOGLE_API_KEY')
    cse_id = os.environ.get('GOOGLE_CSE_ID')

    if not api_key or not cse_id:
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': 'Google API credentials not configured',
            'timestamp': datetime.now().isoformat()
        }

    try:
        # Use protection if available
        if PROTECTION_AVAILABLE:
            protected_cse = ProtectedGoogleCSE(api_key, cse_id)
            results = protected_cse.search(query, num_results=max_results)
            if results.get('error'):
                return {
                    'query': query,
                    'found': 0,
                    'articles': [],
                    'urls': [],
                    'sources_searched': [],
                    'error': results['error'],
                    'timestamp': datetime.now().isoformat()
                }
            articles = results.get('articles', [])
        else:
            # Direct Google CSE call
            service = build('customsearch', 'v1', developerKey=api_key)
            result = service.cse().list(
                q=query,
                cx=cse_id,
                num=min(max_results, 10)
            ).execute()

            articles = []
            for item in result.get('items', []):
                articles.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Google CSE'
                })

        # Format response
        return {
            'query': query,
            'found': len(articles),
            'articles': articles,
            'urls': [article['url'] for article in articles],
            'sources_searched': ['Google CSE'],
            'timestamp': datetime.now().isoformat(),
            'cost_estimate': f'${len(articles) * 0.005:.3f}' if articles else '$0.000'
        }

    except HttpError as e:
        error_details = json.loads(e.content.decode()) if e.content else {}
        error_message = error_details.get('error', {}).get('message', str(e))

        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': f'Google CSE error: {error_message}',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': f'Search error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
