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
        Uses homepage/category scraping as primary method since search is unreliable.
        """
        print(f"Searching Illawarra Mercury for '{query}'...")
        
        urls = []
        seen_urls = set()
        
        # Strategy 1: Homepage and category scraping (most reliable)
        try:
            category_urls = [
                "https://www.illawarramercury.com.au",
                "https://www.illawarramercury.com.au/news/",
                "https://www.illawarramercury.com.au/sport/",
                "https://www.illawarramercury.com.au/news/business/"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            all_story_urls = []
            
            for category_url in category_urls:
                try:
                    resp = requests.get(category_url, headers=headers, timeout=12)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.content, 'lxml')
                    
                    # Find all story links with more comprehensive search
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href:
                            full_url = urljoin("https://www.illawarramercury.com.au", href)
                            # Remove comment links and duplicates
                            if '#comments' not in full_url and full_url not in all_story_urls:
                                all_story_urls.append(full_url)
                
                except Exception as e:
                    print(f"Failed to scrape category {category_url}: {e}")
                    continue
            
            print(f"Found {len(all_story_urls)} total articles from categories")
            
            # Strategy 1a: URL keyword matching with scoring (primary relevance filter)
            query_words = [word.lower() for word in query.split() if len(word) > 2]  # Skip short words
            
            # Score URLs based on relevance
            url_scores = []
            for story_url in all_story_urls:
                url_text = story_url.lower()
                score = 0
                
                # Higher score for exact matches in URL
                for word in query_words:
                    if word in url_text:
                        score += 10
                        # Bonus for word appearing in the story slug (after /story/)
                        if '/story/' in url_text and word in url_text.split('/story/')[-1]:
                            score += 5
                
                if score > 0:
                    url_scores.append((score, story_url))
            
            # Sort by relevance score and take top results
            url_scores.sort(reverse=True, key=lambda x: x[0])
            relevant_urls = [url for score, url in url_scores[:max_results]]
            
            print(f"Found {len(relevant_urls)} relevant URL matches")
            
            if relevant_urls:
                urls.extend(relevant_urls)
                seen_urls.update(relevant_urls)
                print(f"Strategy 1 found {len(urls)} relevant articles")
                return urls
            
            # Strategy 1b: If no URL matches, do limited title analysis only
            print("No URL matches found, checking article titles...")
            
            title_matches = []
            # Only check first 30 articles to keep it fast
            for story_url in all_story_urls[:30]:
                try:
                    resp = requests.get(story_url, headers=headers, timeout=6)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.content, 'lxml')
                        
                        # Get just the title
                        title_text = ""
                        title_elem = soup.find('h1')
                        if title_elem:
                            title_text = title_elem.get_text().lower()
                        
                        # Check if query words appear in title
                        title_score = 0
                        for word in query_words:
                            if word in title_text:
                                title_score += 1
                        
                        if title_score > 0:
                            title_matches.append((title_score, story_url))
                            if len(title_matches) >= max_results:
                                break
                
                except Exception:
                    continue
                
                # Very small delay to be respectful
                time.sleep(0.2)
            
            # Sort title matches by relevance
            title_matches.sort(reverse=True, key=lambda x: x[0])
            title_urls = [url for score, url in title_matches]
            
            print(f"Found {len(title_urls)} title matches")
            
            if title_urls:
                urls.extend(title_urls)
                seen_urls.update(title_urls)
                print(f"Strategy 1 found {len(urls)} articles via title analysis")
                return urls
        
        except Exception as e:
            print(f"Homepage scraping failed: {e}")
        
        # Strategy 2: Try Google search as fallback (only if no results yet)
        if len(urls) == 0:
            try:
                search_query = f"site:illawarramercury.com.au {query}"
                google_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
                
                resp = requests.get(google_url, headers=headers, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'lxml')

                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if '/url?q=' in href:
                        # Extract actual URL from Google redirect
                        match = re.search(r'/url\?q=([^&]+)', href)
                        if match:
                            actual_url = unquote(match.group(1))
                            if 'illawarramercury.com.au/story/' in actual_url and actual_url not in seen_urls:
                                seen_urls.add(actual_url)
                                urls.append(actual_url)
                                if len(urls) >= max_results:
                                    break
                
                print(f"Google search found {len(urls)} articles")

            except Exception as e:
                print(f"Google search fallback failed: {e}")
        
        # Strategy 3: Try DuckDuckGo as last resort (only if still no results)
        if len(urls) == 0:
            try:
                ddg_search_url = "https://html.duckduckgo.com/html/"
                params = {'q': f'site:illawarramercury.com.au {query}'}
                
                resp = requests.get(ddg_search_url, headers=headers, params=params, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'lxml')

                for link in soup.find_all('a', class_='result__a'):
                    href = link.get('href')
                    if href:
                        clean_url = unquote(href)
                        match = re.search(r'uddg=([^&]+)', clean_url)
                        if match:
                            actual_url = unquote(match.group(1))
                            if 'illawarramercury.com.au/story/' in actual_url and actual_url not in seen_urls:
                                seen_urls.add(actual_url)
                                urls.append(actual_url)
                                if len(urls) >= max_results:
                                    break
                
                print(f"DuckDuckGo search found {len(urls)} total articles")

            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
        
        print(f"Final result: {len(urls)} relevant articles found")
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
