#!/usr/bin/env python3
"""
Google CSE News Search API - Vercel Serverless Function
Powered by Google Custom Search Engine for reliable news results
Updated: September 3, 2025 - Fixed function invocation
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
    from .protected_cse import ProtectedGoogleCSE
    PROTECTION_AVAILABLE = True
except ImportError:
    try:
        from protected_cse import ProtectedGoogleCSE
        PROTECTION_AVAILABLE = True
    except ImportError:
        PROTECTION_AVAILABLE = False


def handler(request, response):
    """Vercel serverless function handler"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response.status_code = 200
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
        return ''
    
    # Only allow POST requests
    if request.method != 'POST':
        response.status_code = 405
        response.headers.update({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
        return json.dumps({
            'error': 'Method not allowed. Use POST.',
            'status': 405,
            'timestamp': datetime.now().isoformat()
        })
    
    try:
        # Parse request data
        if hasattr(request, 'get_json'):
            data = request.get_json() or {}
        else:
            # Handle raw request body
            import io
            if hasattr(request, 'body'):
                body = request.body
            elif hasattr(request, 'data'):
                body = request.data
            else:
                body = b'{}'
            
            if isinstance(body, str):
                body = body.encode('utf-8')
            
            try:
                data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {}
        
        # Extract search parameters
        query = data.get('query', '').strip()
        sources = data.get('sources', [])
        max_results = data.get('max_results', 10)
        
        if not query:
            response.status_code = 400
            response.headers.update({
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            })
            return json.dumps({
                'error': 'Query parameter is required',
                'status': 400,
                'timestamp': datetime.now().isoformat()
            })
        
        # Perform search
        search_results = search_news(query, sources, max_results)
        
        # Send response
        response.status_code = 200
        response.headers.update({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
        
        return json.dumps(search_results, ensure_ascii=False)
        
    except Exception as e:
        response.status_code = 500
        response.headers.update({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
        
        return json.dumps({
            'error': f'Internal server error: {str(e)}',
            'status': 500,
            'timestamp': datetime.now().isoformat()
        })

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
            'error': 'Google API client not available - check dependencies',
            'timestamp': datetime.now().isoformat()
        }
    
    # Get API credentials from environment
    api_key = os.environ.get('GOOGLE_API_KEY')
    cse_id = os.environ.get('GOOGLE_CSE_ID')
    
    if not api_key:
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': 'Google API key not configured in environment variables',
            'timestamp': datetime.now().isoformat()
        }
    
    if not cse_id:
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': 'Google CSE ID not configured in environment variables',
            'timestamp': datetime.now().isoformat()
        }
    
    try:
        # Use protection if available
        if PROTECTION_AVAILABLE:
            try:
                protected_cse = ProtectedGoogleCSE(api_key)
                results = protected_cse.search_protected(query, num=max_results)
                
                if not results.get('success', False):
                    return {
                        'query': query,
                        'found': 0,
                        'articles': [],
                        'urls': [],
                        'sources_searched': [],
                        'error': results.get('error', 'Protected search failed'),
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Convert the results format
                articles = []
                for item in results.get('items', []):
                    articles.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Google CSE'
                    })
                    
            except Exception as protection_error:
                # Fall back to direct CSE if protection fails
                return {
                    'query': query,
                    'found': 0,
                    'articles': [],
                    'urls': [],
                    'sources_searched': [],
                    'error': f'Protection module error: {str(protection_error)}',
                    'timestamp': datetime.now().isoformat()
                }
        else:
            # Direct Google CSE call
            try:
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
                    
            except Exception as direct_error:
                return {
                    'query': query,
                    'found': 0,
                    'articles': [],
                    'urls': [],
                    'sources_searched': [],
                    'error': f'Direct CSE error: {str(direct_error)}',
                    'timestamp': datetime.now().isoformat()
                }
        
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
        try:
            error_details = json.loads(e.content.decode()) if e.content else {}
            error_message = error_details.get('error', {}).get('message', str(e))
        except:
            error_message = str(e)
        
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': f'Google CSE HTTP error: {error_message}',
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
