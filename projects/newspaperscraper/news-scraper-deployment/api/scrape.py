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

            urls = data.get('urls', [])
            if not urls or not isinstance(urls, list):
                self.send_error_response(
                    400, 'No URLs provided or URLs not in list format')
                return

            results = []
            scraped_count = 0

            for i, url in enumerate(urls):
                try:
                    print(f"Scraping {i+1}/{len(urls)}: {url}")
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.content, 'html.parser')

                    title = soup.find('h1')
                    date = soup.find('time')

                    # Try to get article content
                    content_selectors = [
                        'div.article-content',
                        'div.story-content',
                        'div.entry-content',
                        'article',
                        'div.post-content',
                        'div.content',
                        'div.article-body',
                        'div.story-body'
                    ]

                    content = ''
                    for selector in content_selectors:
                        content_div = soup.select_one(selector)
                        if content_div:
                            # Get all paragraphs and divs with text content
                            elements = content_div.find_all(
                                ['p', 'h2', 'h3', 'div', 'span'], recursive=False)
                            content_parts = []

                            for elem in elements:
                                # Skip empty elements
                                text = elem.get_text(strip=True)
                                if text and len(text) > 20:  # Skip very short elements
                                    content_parts.append(text)

                            content = ' '.join(content_parts)
                            print(f"Found content using selector: {selector}")
                            break

                    # Fallback to meta description if no content found
                    if not content:
                        preview = soup.find(
                            'meta', attrs={'name': 'description'})
                        if preview:
                            try:
                                content = preview.get('content', '')
                            except (AttributeError, TypeError):
                                content = ''
                        else:
                            paragraphs = soup.find_all('p')[:3]
                            content = ' '.join(
                                [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

                    # Ensure content is a string
                    if not isinstance(content, str):
                        content = str(content)

                    # Get date safely
                    date_str = ''
                    if date:
                        try:
                            # Try to get datetime attribute first
                            date_str = date.get('datetime', '')

                            # If no datetime, get text content
                            if not date_str:
                                date_str = date.get_text(strip=True)
                        except (AttributeError, TypeError):
                            date_str = ''

                    # If no date found in time tag, try meta tags
                    if not date_str:
                        date_meta = soup.find(
                            'meta', attrs={'name': 'pubdate'})
                        if date_meta:
                            date_str = date_meta.get('content', '')
                        else:
                            date_meta = soup.find(
                                'meta', attrs={'property': 'article:published_time'})
                            if date_meta:
                                date_str = date_meta.get('content', '')

                    results.append({
                        'url': url,
                        'title': title.get_text(strip=True) if title else 'No title found',
                        'date': date_str,
                        'content': content[:2000] + '...' if len(content) > 2000 else content
                    })
                    scraped_count += 1

                except requests.exceptions.Timeout:
                    print(f"Timeout scraping: {url}")
                    results.append({'url': url, 'error': 'Request timeout'})
                except requests.exceptions.ConnectionError:
                    print(f"Connection error scraping: {url}")
                    results.append({'url': url, 'error': 'Connection error'})
                except requests.exceptions.HTTPError as e:
                    print(
                        f"HTTP error {e.response.status_code} scraping: {url}")
                    results.append(
                        {'url': url, 'error': f'HTTP {e.response.status_code} error'})
                except Exception as e:
                    print(f"Error scraping {url}: {type(e).__name__}: {e}")
                    results.append({'url': url, 'error': str(e)})

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'scraped': scraped_count,
                'total': len(urls),
                'articles': [r for r in results if 'error' not in r],
                'errors': [r for r in results if 'error' in r]
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Unexpected error in scrape do_POST: {e}")
            self.send_error_response(500, f'Internal server error: {str(e)}')

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
