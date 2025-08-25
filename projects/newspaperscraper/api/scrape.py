# api/scrape.py
from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup

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

        urls = data.get('urls', [])
        if not urls or not isinstance(urls, list):
            self.send_error_response(400, 'No URLs provided')
            return

        results = []
        for url in urls:
            try:
                resp = requests.get(url, timeout=8)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, 'html.parser')
                title = soup.find('h1')
                date = soup.find('time')
                # Try to get a preview/summary
                preview = soup.find('meta', attrs={'name': 'description'})
                if preview:
                    preview_text = preview.get('content', '')
                else:
                    # Fallback: first paragraph
                    p = soup.find('p')
                    preview_text = p.get_text(strip=True) if p else ''
                results.append({
                    'url': url,
                    'title': title.get_text(strip=True) if title else '',
                    'date': date.get('datetime', '') if date else '',
                    'preview': preview_text
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e)
                })

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'results': results}).encode())

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
