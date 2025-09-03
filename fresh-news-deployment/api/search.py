#!/usr/bin/env python3
"""
Google CSE News Search API - Vercel Serverless Function
Powered by Google Custom Search Engine for reliable news results
Updated: September 3, 2025 - Fixed for Vercel BaseHTTPRequestHandler
"""

import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler

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


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for search"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_error(400, 'Invalid JSON in request body')
                return
            
            # Extract search parameters
            query = data.get('query', '').strip()
            sources = data.get('sources', [])
            max_results = data.get('max_results', 10)
            
            if not query:
                self._send_error(400, 'Query parameter is required')
                return
            
            # Perform search
            search_results = search_news(query, sources, max_results)
            
            # Send successful response
            self._send_json_response(200, search_results)
            
        except Exception as e:
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def do_GET(self):
        """Handle GET requests - not allowed"""
        self._send_error(405, 'Method not allowed. Use POST.')
    
    def _send_json_response(self, status_code, data):
        """Send JSON response with proper headers"""
        response_data = json.dumps(data, ensure_ascii=False)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        error_data = {
            'error': message,
            'status': status_code,
            'timestamp': datetime.now().isoformat()
        }
        self._send_json_response(status_code, error_data)


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
                    'error': f'Google CSE API error: {str(direct_error)}',
                    'timestamp': datetime.now().isoformat()
                }
        
        # Process results
        urls = [article['url'] for article in articles]
        
        return {
            'query': query,
            'found': len(articles),
            'articles': articles,
            'urls': urls,
            'sources_searched': ['Google CSE'],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'query': query,
            'found': 0,
            'articles': [],
            'urls': [],
            'sources_searched': [],
            'error': f'Search operation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }