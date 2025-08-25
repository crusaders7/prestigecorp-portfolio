# filepath: projects/newspaperscraper/api/search.py
from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        query = data.get('query', '').strip()
        max_results = min(int(data.get('max_results', 10)), 20)

        if not query:
            self.send_error_response(400, 'Please enter a search term')
            return

        article_urls = self.search_illawarra_mercury(query, max_results)

        if not article_urls:
            self.send_error_response(404, f'No articles found for \"{query}\" in Illawarra Mercury.')
            return

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

    def search_illawarra_mercury(self, query, max_results=7):
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
            for link in soup.select('a[href*="/story/"]'):
                title_text = link.get_text(strip=True)
                href = link.get('href', '')
                if href and '/story/' in href:
                    if query.lower() in title_text.lower():
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            if len(article_links) >= max_results:
                                break
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