from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import time

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '').strip()
            max_results = min(data.get('max_results', 10), 20)
            
            if not query:
                self.send_error_response(400, 'Please enter a search term')
                return
            
            # Search Illawarra Mercury
            article_urls = self.search_illawarra_mercury(query, max_results)
            
            if not article_urls:
                self.send_error_response(404, f'No articles found for "{query}" in Illawarra Mercury.')
                return
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'query': query,
                'found': len(article_urls),
                'urls': article_urls,
                'sources_searched': ['mercury']
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Search error: {e}")
            self.send_error_response(500, f'Search failed: {str(e)}')
    
    def search_illawarra_mercury(self, query, max_results=7):
        """Search Illawarra Mercury"""
        try:
            base_url = "https://www.illawarramercury.com.au"
            search_url = f"{base_url}/search/?q={quote_plus(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers, timeout=8)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []
            
            # Try multiple selectors
            selectors = [
                'a[href*="/story/"]',
                'h2 a, h3 a',
                'article a',
                '.search-results a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    if href and '/story/' in href:
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            if len(article_links) >= max_results:
                                return article_links
            
            time.sleep(0.5)
            return article_links
            
        except Exception as e:
            print(f"Illawarra Mercury search error: {e}")
            return []
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
