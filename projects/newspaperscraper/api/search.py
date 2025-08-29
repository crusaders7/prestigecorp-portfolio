from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
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

            sources = data.get('sources', ['mercury', 'abc', 'guardian'])
            if not isinstance(sources, list):
                sources = ['mercury', 'abc', 'guardian']

            if not query:
                self.send_error_response(400, 'Please enter a search term')
                return

            article_urls = []
            sources_searched = []

            # Search Illawarra Mercury
            if 'mercury' in sources:
                article_urls += self.search_illawarra_mercury(
                    query, max_results)
                sources_searched.append('mercury')

            # Search ABC News
            if 'abc' in sources:
                article_urls += self.search_abc_news(query, max_results)
                sources_searched.append('abc')

            # Search The Guardian Australia
            if 'guardian' in sources:
                article_urls += self.search_the_guardian(query, max_results)
                sources_searched.append('guardian')

            if not article_urls:
                self.send_error_response(
                    404, f'No articles found for "{query}" across all sources.')
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'query': query,
                'found': len(article_urls),
                'urls': article_urls,
                'sources_searched': sources_searched
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

            print(f"Searching Illawarra Mercury: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # More specific selector for search result items
            for result in soup.select('.css-1s72p3j'):
                link_tag = result.find('a', href=True)
                if link_tag:
                    title_text = link_tag.get_text(strip=True)
                    href = link_tag['href']

                    # Check if it's a valid story link and relevant
                    if '/story/' in href:
                        query_words = query.lower().split()
                        if any(word in title_text.lower() for word in query_words):
                            full_url = urljoin(base_url, href)
                            if full_url not in article_links:
                                article_links.append(full_url)
                                if len(article_links) >= max_results:
                                    break

            print(
                f"Illawarra Mercury result: {len(article_links)} articles found")
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

    def search_abc_news(self, query, max_results=7):
        try:
            base_url = "https://www.abc.net.au"
            # Use the main search page for better results
            search_url = f"https://www.abc.net.au/news/search?query={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Tool)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            print(f"Searching ABC News: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # Selector for ABC News search results
            for result in soup.select('div._1E3hT'):
                link_tag = result.find('a', href=True)
                if link_tag:
                    title_text = link_tag.get_text(strip=True)
                    href = link_tag['href']

                    if '/news/' in href:
                        query_words = query.lower().split()
                        if any(word in title_text.lower() for word in query_words):
                            full_url = urljoin(base_url, href)
                            if full_url not in article_links:
                                article_links.append(full_url)
                                if len(article_links) >= max_results:
                                    break

            print(f"ABC News result: {len(article_links)} articles found")
            return article_links

        except requests.exceptions.Timeout:
            print(f"Timeout error while searching ABC News for: {query}")
            return []
        except requests.exceptions.ConnectionError:
            print(f"Connection error while searching ABC News for: {query}")
            return []
        except requests.exceptions.HTTPError as e:
            print(
                f"HTTP error {e.response.status_code} while searching ABC News for: {query}")
            return []
        except Exception as e:
            print(
                f"Unexpected error in ABC News search: {type(e).__name__}: {e}")
            return []

    def search_the_guardian(self, query, max_results=7):
        try:
            base_url = "https://www.theguardian.com"
            # Use general search
            search_url = f"https://www.theguardian.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Tool)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            print(f"Searching The Guardian: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # Selector for Guardian search results
            for result in soup.select('div.fc-item__container'):
                link_tag = result.find(
                    'a', {'class': 'fc-item__link'}, href=True)
                if link_tag:
                    title_text = link_tag.get_text(strip=True)
                    href = link_tag['href']

                    # Check if it's a news article and relevant
                    if 'theguardian.com/' in href:  # Check if it's a full URL
                        query_words = query.lower().split()
                        if any(word in title_text.lower() for word in query_words):
                            full_url = href  # It's already a full URL
                            if full_url not in article_links:
                                article_links.append(full_url)
                                if len(article_links) >= max_results:
                                    break

            print(f"The Guardian result: {len(article_links)} articles found")
            return article_links

        except requests.exceptions.Timeout:
            print(f"Timeout error while searching The Guardian for: {query}")
            return []
        except requests.exceptions.ConnectionError:
            print(
                f"Connection error while searching The Guardian for: {query}")
            return []
        except requests.exceptions.HTTPError as e:
            print(
                f"HTTP error {e.response.status_code} while searching The Guardian for: {query}")
            return []
        except Exception as e:
            print(
                f"Unexpected error in The Guardian search: {type(e).__name__}: {e}")
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
