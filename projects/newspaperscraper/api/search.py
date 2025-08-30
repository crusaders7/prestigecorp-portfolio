from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, unquote
import time
import re


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

            # Default to 'mercury' if not provided
            sources = data.get('sources', ['mercury'])

            if not query:
                self.send_error_response(400, 'Please enter a search term')
                return

            all_urls = []
            errors = []
            sources_searched = []

            if 'mercury' in sources:
                try:
                    mercury_urls = self.search_illawarra_mercury(
                        query, max_results)
                    all_urls.extend(mercury_urls)
                    sources_searched.append('Illawarra Mercury')
                except Exception as e:
                    print(f"Error searching Illawarra Mercury: {e}")
                    errors.append(
                        {'source': 'Illawarra Mercury', 'error': str(e)})

            if 'abc' in sources:
                try:
                    abc_urls = self.search_abc_news(query, max_results)
                    all_urls.extend(abc_urls)
                    sources_searched.append('ABC News')
                except Exception as e:
                    print(f"Error searching ABC News: {e}")
                    errors.append({'source': 'ABC News', 'error': str(e)})

            if 'guardian' in sources:
                try:
                    guardian_urls = self.search_the_guardian(
                        query, max_results)
                    all_urls.extend(guardian_urls)
                    sources_searched.append('The Guardian')
                except Exception as e:
                    print(f"Error searching The Guardian: {e}")
                    errors.append({'source': 'The Guardian', 'error': str(e)})

            # Remove duplicates while preserving order
            seen_urls = set()
            unique_urls = []
            for url in all_urls:
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_urls.append(url)

            # Limit the results to max_results
            final_urls = unique_urls[:max_results]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'query': query,
                'found': len(final_urls),
                'urls': final_urls,
                'sources_searched': sources_searched
            }
            if errors:
                response['errors'] = errors
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error_response(500, f'Internal server error: {str(e)}')

    def search_illawarra_mercury(self, query, max_results):
        """
        Searches the Illawarra Mercury website using a multi-strategy approach.
        It first attempts a direct search and falls back to DuckDuckGo if needed.
        """
        try:
            # Strategy 1: Direct Search
            direct_search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            resp = requests.get(direct_search_url, headers=headers, timeout=12)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.content, 'lxml')
            
            urls = []
            seen_urls = set()

            # This selector is based on the provided HTML and may need updates if the site changes.
            for link in soup.select('.story-block__headline a'):
                if len(urls) >= max_results:
                    break
                href = link.get('href')
                if href:
                    full_url = urljoin("https://www.illawarramercury.com.au", href)
                    if full_url not in seen_urls and 'illawarramercury.com.au/story/' in full_url:
                        seen_urls.add(full_url)
                        urls.append(full_url)
            
            if urls:
                print(f"Direct search succeeded with {len(urls)} results.")
                return urls

        except Exception as e:
            print(f"Direct search failed: {e}. Falling back to DuckDuckGo.")

        # Strategy 2: Fallback to DuckDuckGo
        try:
            ddg_search_url = "https://html.duckduckgo.com/html/"
            params = {'q': f'site:illawarramercury.com.au {query}'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            resp = requests.get(ddg_search_url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'lxml')

            urls = []
            seen_urls = set()

            for link in soup.find_all('a', class_='result__a'):
                if len(urls) >= max_results:
                    break
                href = link.get('href')
                if href:
                    clean_url = unquote(href)
                    match = re.search(r'uddg=([^&]+)', clean_url)
                    if match:
                        actual_url = unquote(match.group(1))
                        if actual_url not in seen_urls and 'illawarramercury.com.au/story/' in actual_url:
                            seen_urls.add(actual_url)
                            urls.append(actual_url)
            
            print(f"DuckDuckGo fallback search found {len(urls)} results.")
            return urls

        except Exception as e:
            print(f"DuckDuckGo fallback search also failed: {e}")
            return []

    def search_abc_news(self, query, max_results):
        """Searches ABC News for a given query."""
        try:
            base_url = "https://www.abc.net.au"
            search_url = f"https://www.abc.net.au/news/search?query={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Tool)'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # A more robust selector for ABC News search results
            for result in soup.select('a[data-component="Link"]'):
                href = result.get('href', '')
                if href and '/news/' in href and 'live-updates' not in href:
                    full_url = urljoin(base_url, href)
                    if full_url not in article_links:
                        article_links.append(full_url)
                        if len(article_links) >= max_results:
                            break
            return article_links
        except Exception as e:
            print(f"Error in ABC News search: {e}")
            return []

    def search_the_guardian(self, query, max_results):
        """Searches The Guardian for a given query."""
        try:
            base_url = "https://www.theguardian.com"
            search_url = f"https://www.theguardian.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Tool)'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # A more robust selector for Guardian search results
            for result in soup.select('a[data-testid="result-title-a"]'):
                href = result.get('href', '')
                if href:
                    if href not in article_links:
                        article_links.append(href)
                        if len(article_links) >= max_results:
                            break
            return article_links
        except Exception as e:
            print(f"Error in The Guardian search: {e}")
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
