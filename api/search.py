from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the projects/newspaperscraper/api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'projects', 'newspaperscraper', 'api'))

# Import our protected Google CSE
try:
    from protected_cse import ProtectedGoogleCSE
    CSE_AVAILABLE = True
except ImportError:
    CSE_AVAILABLE = False


class handler(BaseHTTPRequestHandler):
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

            # Use Google CSE if available
            if CSE_AVAILABLE and query:
                try:
                    cse = ProtectedGoogleCSE()
                    articles = cse.search_simple(query, max_results=max_results)
                    
                    # Convert to expected format
                    formatted_articles = []
                    for article in articles:
                        formatted_articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'snippet': article.get('snippet', ''),
                            'source': 'Illawarra Mercury',
                            'domain': article.get('domain', 'illawarramercury.com.au')
                        })
                    
                    response = {
                        'status': 'success',
                        'query': query,
                        'found': len(formatted_articles),
                        'articles': formatted_articles,
                        'sources_searched': ['illawarra_mercury'],
                        'api_protection': 'active',
                        'urls': [article['url'] for article in formatted_articles]
                    }
                    
                except Exception as e:
                    response = {
                        'status': 'error',
                        'query': query,
                        'found': 0,
                        'articles': [],
                        'error': f'Search failed: {str(e)}',
                        'sources_searched': [],
                        'urls': []
                    }
            else:
                # Fallback response when CSE not available
                response = {
                    'status': 'fallback',
                    'query': query,
                    'found': 0,
                    'articles': [],
                    'sources_searched': [],
                    'message': 'Google CSE not available in this deployment',
                    'urls': []
                }

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'error',
                'error': str(e),
                'found': 0,
                'articles': [],
                'urls': []
            }

        # Send the response
        self.wfile.write(json.dumps(response).encode('utf-8'))
