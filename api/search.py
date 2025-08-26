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
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, 'No data received')
                return

            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error_response(400, f'Invalid JSON data: {str(e)}')
                return
            except UnicodeDecodeError as e:
                self.send_error_response(
                    400, f'Invalid UTF-8 encoding: {str(e)}')
                return

            query = data.get('query', '').strip()

            try:
                max_results = min(int(data.get('max_results', 10)), 20)
            except (ValueError, TypeError):
                max_results = 10

            if not query:
                self.send_error_response(400, 'Please enter a search term')
                return

            article_urls = self.search_illawarra_mercury(query, max_results)

            if not article_urls:
                self.send_error_response(
                    404, f'No articles found for "{query}" in Illawarra Mercury.')
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

        except Exception as e:
            print(f"Unexpected error in do_POST: {e}")
            self.send_error_response(500, f'Internal server error: {str(e)}')

    def search_illawarra_mercury(self, query, max_results=7):
        try:
            base_url = "https://www.illawarramercury.com.au"
            search_url = f"{base_url}/search/?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            print(f"Searching URL: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            links = soup.select('a[href*="/story/"]')
            print(f"Found {len(links)} potential article links")

            for link in links:
                title_text = link.get_text(strip=True)
                href = link.get('href', '')
                if href and isinstance(href, str) and '/story/' in href:
                    query_words = query.lower().split()
                    if any(word in title_text.lower() for word in query_words):
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            print(f"Added article: {title_text[:50]}...")
                            if len(article_links) >= max_results:
                                break

            print(f"Final result: {len(article_links)} articles found")
            return article_links

        except requests.exceptions.Timeout:
            print(f"Timeout error while searching for: {query}")
            return []
        except requests.exceptions.ConnectionError:
            print(f"Connection error while searching for: {query}")
            return []
        except requests.exceptions.HTTPError as e:
            print(
                f"HTTP error {e.response.status_code} while searching for: {query}")
            return []
        except Exception as e:
            print(
                f"Unexpected error in Illawarra Mercury search: {type(e).__name__}: {e}")
            return []

    def send_error_response(self, code, message):
        try:
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'error': message}
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            print(f"Failed to send error response: {e}")
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Internal server error')
            except:
                print(
                    f"Critical error - unable to send any response: {message}")
