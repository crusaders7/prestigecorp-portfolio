from http.server import BaseHTTPRequestHandler
import json
import requests
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'ready',
            'message': 'News search API endpoint ready',
            'methods': ['POST'],
            'usage': 'Send POST request with {"query": "search terms"}'
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract search parameters
            query = request_data.get('query', '')
            max_results = min(request_data.get('max_results', 10), 10)  # Limit to 10 for cost control
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Direct Google CSE API integration with basic protection
            if query and len(query.strip()) >= 2:
                try:
                    # Google CSE configuration
                    api_key = "AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0"
                    cse_id = "012527284968046999840:zzi3qgsoibq"
                    api_endpoint = "https://www.googleapis.com/customsearch/v1"
                    
                    # Make Google CSE API call
                    params = {
                        'key': api_key,
                        'cx': cse_id,
                        'q': query.strip(),
                        'num': max_results,
                        'safe': 'off',
                        'fields': 'items(title,link,snippet,displayLink),searchInformation(totalResults,searchTime)'
                    }
                    
                    cse_response = requests.get(api_endpoint, params=params, timeout=30)
                    
                    if cse_response.status_code == 200:
                        data = cse_response.json()
                        items = data.get('items', [])
                        
                        # Convert to expected format
                        formatted_articles = []
                        article_urls = []
                        
                        for item in items:
                            article_url = item.get('link', '')
                            formatted_articles.append({
                                'title': item.get('title', ''),
                                'url': article_url,
                                'snippet': item.get('snippet', ''),
                                'source': 'Illawarra Mercury',
                                'domain': item.get('displayLink', 'illawarramercury.com.au')
                            })
                            article_urls.append(article_url)
                        
                        response = {
                            'status': 'success',
                            'query': query,
                            'found': len(formatted_articles),
                            'articles': formatted_articles,
                            'sources_searched': ['illawarra_mercury'],
                            'total_results': data.get('searchInformation', {}).get('totalResults', '0'),
                            'api_protection': 'active',
                            'urls': article_urls
                        }
                    else:
                        response = {
                            'status': 'api_error',
                            'query': query,
                            'found': 0,
                            'articles': [],
                            'error': f'Google CSE API returned status {cse_response.status_code}',
                            'sources_searched': [],
                            'urls': []
                        }
                        
                except Exception as e:
                    response = {
                        'status': 'search_error',
                        'query': query,
                        'found': 0,
                        'articles': [],
                        'error': f'Search failed: {str(e)}',
                        'sources_searched': [],
                        'urls': []
                    }
            else:
                # Invalid query
                response = {
                    'status': 'invalid_query',
                    'query': query,
                    'found': 0,
                    'articles': [],
                    'sources_searched': [],
                    'message': 'Query must be at least 2 characters',
                    'urls': []
                }

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'server_error',
                'error': str(e),
                'found': 0,
                'articles': [],
                'urls': []
            }

        # Send the response
        self.wfile.write(json.dumps(response).encode('utf-8'))
