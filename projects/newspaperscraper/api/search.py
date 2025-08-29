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

            # Try multiple selectors to find article links
            links = soup.select('a[href*="/story/"]')
            if not links:
                links = soup.select('h3 a')
            if not links:
                links = soup.select('.search-result__title a')

            print(f"Found {len(links)} potential article links")

            for link in links:
                title_text = link.get_text(strip=True)
                href = link.get('href', '')
                if href and '/story/' in href:
                    # More flexible matching - check if any query word is in the title
                    query_words = query.lower().split()
                    if any(word in title_text.lower() for word in query_words):
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            print(f"Added article: {title_text[:50]}...")
                            if len(article_links) >= max_results:
                                break

            # If still no results, try a more lenient approach
            if not article_links:
                print("Trying lenient approach to find article links")
                all_links = soup.find_all('a', href=True)
                query_words = query.lower().split()

                for link in all_links:
                    title_text = link.get_text(strip=True)
                    href = link.get('href', '')

                    # Check if it's likely an article link
                    if href and ('/story/' in href or '/article/' in href or
                                 any(word in title_text.lower() for word in query_words)):
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            print(
                                f"Added article (lenient): {title_text[:50]}...")
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
            # Use HTML search instead of JSON API
            search_url = f"https://www.abc.net.au/news/sitemap/?queries={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Tool)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            print(f"Searching ABC News: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # Try multiple selectors for ABC News
            selectors = [
                'a[href*="/news/"]',
                '.story-headline a',
                '.content-item__link',
                'h3 a',
                '.teaser-link'
            ]

            links = []
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    print(
                        f"Found {len(links)} links using selector: {selector}")
                    break

            query_words = [word.lower() for word in query.split()]

            for link in links:
                title_text = link.get_text(strip=True)
                href = link.get('href', '')

                if href and '/news/' in href:
                    # Check if query words match title
                    if any(word in title_text.lower() for word in query_words):
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            print(f"Added ABC article: {title_text[:50]}...")
                            if len(article_links) >= max_results:
                                break

            print(f"ABC News result: {len(article_links)} articles found")
            time.sleep(1)  # Rate limiting
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
            # Use direct website search instead of API
            search_url = f"https://www.theguardian.com/australia-news/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Tool)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            print(f"Searching The Guardian: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []

            # Try multiple selectors for Guardian
            selectors = [
                'a[data-link-name="article"]',
                '.fc-item__link',
                '.u-faux-block-link__overlay',
                'h3 a',
                '.headline-link'
            ]

            links = []
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    print(
                        f"Found {len(links)} links using selector: {selector}")
                    break

            query_words = [word.lower() for word in query.split()]

            for link in links:
                title_text = link.get_text(strip=True)
                href = link.get('href', '')

                if href and ('/australia-news/' in href or '/world/' in href):
                    # Check if query words match title
                    if any(word in title_text.lower() for word in query_words):
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            print(
                                f"Added Guardian article: {title_text[:50]}...")
                            if len(article_links) >= max_results:
                                break

            print(f"The Guardian result: {len(article_links)} articles found")
            time.sleep(1)  # Rate limiting
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
