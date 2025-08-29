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
        Searches Illawarra Mercury for articles.
        First, it tries the native site search (which uses Google Custom Search).
        If that fails, it falls back to using DuckDuckGo.
        """
        try:
            print("Attempting native search for Illawarra Mercury...")
            urls = self._search_mercury_native(query, max_results)
            if not urls:
                print("Native search returned no results, trying fallback.")
                # This is not an exception, just empty results, so we fall back.
                return self._search_mercury_duckduckgo(query, max_results)
            print(f"Native search found {len(urls)} results.")
            return urls
        except Exception as e:
            print(
                f"Native search failed: {e}. Falling back to DuckDuckGo search.")
            return self._search_mercury_duckduckgo(query, max_results)

    def _search_mercury_native(self, query, max_results):
        search_url = f"https://www.illawarramercury.com.au/search/?q={requests.utils.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        print(f"Requesting native search URL: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        # Selectors for Google Custom Search Engine results
        for result_elem in soup.select('div.gsc-webResult.gsc-result'):
            if len(results) >= max_results:
                break

            title_elem = result_elem.select_one('a.gs-title')
            if title_elem and title_elem.has_attr('href'):
                url = title_elem['href']
                # Ensure it's a valid and on-site URL
                if url.startswith('http') and 'illawarramercury.com.au/story/' in url:
                    # Clean up tracking parameters
                    url = url.split('?')[0]
                    if url not in results:
                        results.append(url)

        return results

    def _search_mercury_duckduckgo(self, query, max_results):
        """Searches the Illawarra Mercury website for a given query using DuckDuckGo."""
        urls = []
        seen_urls = set()

        # Start with a GET request to get the 's' parameter
        search_url = "https://html.duckduckgo.com/html/"
        params = {'q': f'site:illawarramercury.com.au {query}'}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

        s = ''
        vqd = ''
        # Make the initial request to get the vqd token
        try:
            resp = requests.get(search_url, headers=headers, params=params)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'lxml')

            # Extract vqd from the form
            vqd_input = soup.find('input', attrs={'name': 'vqd'})
            if vqd_input:
                vqd = vqd_input['value']

        except requests.exceptions.RequestException as e:
            print(f"Initial DDG search request failed: {e}")
            return []

        # Now, start paginating with POST requests
        while len(urls) < max_results:
            data = {
                'q': f'site:illawarramercury.com.au {query}',
                's': s,
                'nextParams': '',
                'v': 'l',
                'o': 'json',
                'vqd': vqd,
                'kl': 'wt-wt'
            }

            try:
                resp = requests.post(search_url, headers=headers, data=data)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'lxml')

                page_urls = []
                for link in soup.find_all('a', class_='result__a'):
                    href = link.get('href')
                    if href:
                        # Decode URL-encoded string
                        clean_url = unquote(href)
                        # Extract the actual URL from the DDG redirect
                        match = re.search(r'uddg=([^&]+)', clean_url)
                        if match:
                            actual_url = unquote(match.group(1))
                            if actual_url not in seen_urls and 'illawarramercury.com.au/story/' in actual_url:
                                seen_urls.add(actual_url)
                                page_urls.append(actual_url)

                if not page_urls:
                    break  # No more results

                urls.extend(page_urls)

                # Find the 's' value for the next page
                next_form = soup.find('form', class_='next_form')
                if next_form:
                    s_input = next_form.find('input', {'name': 's'})
                    if s_input:
                        s = s_input['value']
                    else:
                        break  # No more pages
                else:
                    break

            except requests.exceptions.RequestException as e:
                print(f"DDG pagination request failed: {e}")
                break

        return urls[:max_results]

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
