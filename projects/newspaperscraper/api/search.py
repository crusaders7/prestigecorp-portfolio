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

            if not query:
                self.send_error_response(400, 'Please enter a search term')
                return

            # As requested, only search Illawarra Mercury for now.
            article_urls = self.search_illawarra_mercury(query, max_results)
            sources_searched = ['mercury']

            if not article_urls:
                self.send_error_response(
                    404, f'No articles found for "{query}" on Illawarra Mercury.')
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
        """
        Searches the Illawarra Mercury using DuckDuckGo's HTML search to avoid direct scraping issues.
        """
        try:
            search_query = f"site:illawarramercury.com.au {query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://duckduckgo.com/'
            }
            
            # Using DuckDuckGo's HTML endpoint
            ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}"
            
            response = requests.get(ddg_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            article_links = []
            # Links are in divs with class 'result'
            for result in soup.find_all('a', class_='result__a', href=True):
                href = result['href']
                
                # DuckDuckGo uses a redirect, we need to clean the URL
                if 'duckduckgo.com/y.js' in href:
                    href = unquote(href.split('uddg=')[1].split('&')[0])

                # Ensure it's a story and not a category/tag page
                if 'illawarramercury.com.au/story/' in href:
                    if href not in article_links:
                        article_links.append(href)
                        if len(article_links) >= max_results:
                            break
            
            return article_links
        except Exception as e:
            print(f"Error in Illawarra Mercury (DuckDuckGo) search: {e}")
            return []

    # The other search functions are no longer called, but we can leave them here
    # in case they are needed in the future.
    def search_abc_news(self, query, max_results=7):
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

            # Updated selector for ABC News search results
            for result in soup.select('a[data-component="Link"]'):
                title_text = result.get_text(strip=True)
                href = result.get('href', '')
                if href and '/news/' in href and 'live-updates' not in href:
                    query_words = query.lower().split()
                    if any(word in title_text.lower() for word in query_words):
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                            if len(article_links) >= max_results:
                                break
            return article_links
        except Exception as e:
            print(f"Error in ABC News search: {e}")
            return []

    def search_the_guardian(self, query, max_results=7):
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

            # Updated selector for Guardian search results
            for result in soup.select('a[data-testid="result-title-a"]'):
                title_text = result.get_text(strip=True)
                href = result.get('href', '')
                if href:
                    query_words = query.lower().split()
                    if any(word in title_text.lower() for word in query_words):
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
