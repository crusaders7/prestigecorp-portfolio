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

                    # Enhanced title extraction
                    title_text = ''
                    
                    # Method 1: Try h1 elements
                    h1_elements = soup.find_all('h1')
                    for h1 in h1_elements:
                        title_candidate = h1.get_text(strip=True)
                        if title_candidate and len(title_candidate) > 10:
                            title_text = title_candidate
                            break
                    
                    # Method 2: Try meta title tags
                    if not title_text:
                        meta_title = soup.find('meta', attrs={'property': 'og:title'})
                        if meta_title:
                            title_text = meta_title.get('content', '')
                        else:
                            page_title = soup.find('title')
                            if page_title:
                                title_text = page_title.get_text(strip=True)
                    
                    # Method 3: Look for title in common classes
                    if not title_text:
                        title_selectors = [
                            '.article-title',
                            '.post-title',
                            '.entry-title',
                            '.story-title',
                            '[class*="title"]'
                        ]
                        
                        for selector in title_selectors:
                            title_elem = soup.select_one(selector)
                            if title_elem:
                                title_candidate = title_elem.get_text(strip=True)
                                if title_candidate and len(title_candidate) > 10:
                                    title_text = title_candidate
                                    break

                    # Enhanced content selectors for better article extraction
                    content_selectors = [
                        'div.article-content',
                        'div.story-content', 
                        'div.entry-content',
                        'div.post-content',
                        'div.content',
                        'div.article-body',
                        'div.story-body',
                        'div.field-item',
                        'div.node-content',
                        'div.article-text',
                        'div.content-body',
                        'div.main-content',
                        'section.article-body',
                        'section.story-body',
                        'article .content',
                        'article main',
                        '.article-wrapper',
                        '.story-wrapper',
                        '.post-body',
                        '.entry-body',
                        'main article',
                        '[class*="article-content"]',
                        '[class*="story-content"]',
                        '[class*="post-content"]'
                    ]

                    content = ''
                    content_found = False
                    
                    # Try each selector until we find substantial content
                    for selector in content_selectors:
                        try:
                            content_div = soup.select_one(selector)
                            if content_div:
                                # Method 1: Get all text content recursively
                                full_text = content_div.get_text(separator='\n', strip=True)
                                
                                # Method 2: Get paragraphs specifically
                                paragraphs = content_div.find_all(['p', 'div'], recursive=True)
                                paragraph_texts = []
                                
                                for p in paragraphs:
                                    # Skip elements with no text or very short text
                                    text = p.get_text(strip=True)
                                    if text and len(text) > 30:
                                        # Skip navigation, ads, etc.
                                        if not any(skip_word in text.lower() for skip_word in 
                                                 ['subscribe', 'advertisement', 'click here', 'read more', 'share this', 'follow us']):
                                            paragraph_texts.append(text)
                                
                                # Use the method that gives us more substantial content
                                if len(full_text) > len(' '.join(paragraph_texts)):
                                    content = full_text
                                else:
                                    content = ' '.join(paragraph_texts)
                                
                                # If we found substantial content (more than 200 chars), use it
                                if len(content) > 200:
                                    print(f"Found content using selector: {selector} ({len(content)} chars)")
                                    content_found = True
                                    break
                        except Exception as selector_error:
                            print(f"Error with selector {selector}: {selector_error}")
                            continue

                    # Enhanced fallback methods if no content found
                    if not content_found or len(content) < 100:
                        print("Using fallback content extraction methods")
                        
                        # Fallback 1: Try to find main content area
                        main_areas = soup.find_all(['main', 'article', '[role="main"]'])
                        for main_area in main_areas:
                            paragraphs = main_area.find_all('p')
                            if len(paragraphs) >= 3:
                                fallback_content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                                if len(fallback_content) > len(content):
                                    content = fallback_content
                                    break
                        
                        # Fallback 2: Get all paragraphs from the entire page
                        if len(content) < 100:
                            all_paragraphs = soup.find_all('p')
                            good_paragraphs = []
                            for p in all_paragraphs:
                                text = p.get_text(strip=True)
                                if len(text) > 50 and not any(skip in text.lower() for skip in 
                                                            ['cookie', 'subscribe', 'newsletter', 'advertisement']):
                                    good_paragraphs.append(text)
                                if len(good_paragraphs) >= 8:  # Limit to avoid too much content
                                    break
                            if good_paragraphs:
                                content = ' '.join(good_paragraphs)
                        
                        # Fallback 3: Meta description as last resort
                        if len(content) < 50:
                            meta_desc = soup.find('meta', attrs={'name': 'description'})
                            if meta_desc:
                                content = meta_desc.get('content', '')

                    # Ensure content is a string
                    if not isinstance(content, str):
                        content = str(content)

                    # Enhanced date extraction
                    date_str = ''
                    
                    # Method 1: Look for time elements with datetime attribute
                    time_elements = soup.find_all('time')
                    for time_elem in time_elements:
                        if time_elem.get('datetime'):
                            date_str = time_elem.get('datetime')
                            break
                        elif time_elem.get_text(strip=True):
                            date_str = time_elem.get_text(strip=True)
                            break
                    
                    # Method 2: Try various meta tags for date
                    if not date_str:
                        date_meta_selectors = [
                            ('meta', {'name': 'pubdate'}),
                            ('meta', {'property': 'article:published_time'}),
                            ('meta', {'name': 'article:published_time'}),
                            ('meta', {'property': 'article:published'}),
                            ('meta', {'name': 'date'}),
                            ('meta', {'property': 'og:updated_time'}),
                            ('meta', {'name': 'created'}),
                            ('meta', {'itemprop': 'datePublished'}),
                            ('meta', {'itemprop': 'dateCreated'})
                        ]
                        
                        for tag, attrs in date_meta_selectors:
                            meta_tag = soup.find(tag, attrs=attrs)
                            if meta_tag and meta_tag.get('content'):
                                date_str = meta_tag.get('content')
                                break
                    
                    # Method 3: Look for date in common CSS classes
                    if not date_str:
                        date_selectors = [
                            '.published-date',
                            '.post-date', 
                            '.article-date',
                            '.entry-date',
                            '.date',
                            '.timestamp',
                            '.publish-date',
                            '[class*="date"]',
                            '[class*="time"]'
                        ]
                        
                        for selector in date_selectors:
                            date_elem = soup.select_one(selector)
                            if date_elem:
                                date_text = date_elem.get_text(strip=True)
                                if date_text and len(date_text) < 50:  # Reasonable date length
                                    date_str = date_text
                                    break

                    results.append({
                        'url': url,
                        'title': title_text if title_text else 'No title found',
                        'date': date_str,
                        'content': content,  # Return full content without truncation
                        'content_length': len(content)  # Add content length for reference
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
