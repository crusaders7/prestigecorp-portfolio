#!/usr/bin/env python3
"""
Google CSE News Search API - Vercel Serverless Function
Powered by Google Custom Search Engine for reliable news results
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
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

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Reject GET requests - API only accepts POST"""
        self.send_response(501)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = """
        <h1>Error response</h1>
        <p>Error code: 501</p>
        <p>Message: Unsupported method ('GET').</p>
        <p>Error code explanation: 501 - Server does not support this operation.</p>
        """
        self.wfile.write(response.encode())

    def do_POST(self):
        """Handle POST requests for news search"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, 'No data received')
                return

            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.send_error_response(400, f'Invalid JSON data: {str(e)}')
                return

            # Extract search parameters
            query = data.get('query', '').strip()
            sources = data.get('sources', [])
            max_results = data.get('max_results', 10)

            if not query:
                self.send_error_response(400, 'Query parameter is required')
                return

            # Perform search
            search_results = self.search_news(query, sources, max_results)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(search_results, indent=2, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            self.send_error_response(500, f'Internal server error: {str(e)}')

    def search_news(self, query, sources, max_results):
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

    def send_error_response(self, status_code, message):
        """Send an error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'error': message,
            'status': status_code,
            'timestamp': datetime.now().isoformat()
        }
        
        response = json.dumps(error_response, indent=2)
        self.wfile.write(response.encode('utf-8'))
