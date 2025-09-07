import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for article scraping"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for scraping"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_error(400, 'Invalid JSON in request body')
                return
            
            urls = data.get('urls', [])
            if not urls or not isinstance(urls, list):
                self._send_error(400, 'No URLs provided or URLs not in list format')
                return
            
            # Scrape articles
            results = scrape_articles(urls)
            
            # Send successful response
            self._send_json_response(200, results)
            
        except Exception as e:
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def do_GET(self):
        """Handle GET requests - not allowed"""
        self._send_error(405, 'Method not allowed. Use POST.')
    
    def _send_json_response(self, status_code, data):
        """Send JSON response with proper headers"""
        response_data = json.dumps(data, ensure_ascii=False)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        error_data = {
            'error': message,
            'status': status_code,
            'timestamp': datetime.now().isoformat()
        }
        self._send_json_response(status_code, error_data)


def scrape_articles(urls):
    """Scrape articles from provided URLs"""
    results = []
    scraped_count = 0
    
    for i, url in enumerate(urls):
        try:
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            resp = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')

            # Enhanced content extraction with better filtering
            content_found = False
            content = ''
            
            # PRIORITY 1: Try JSON-LD structured data extraction
            json_ld_content = ''
            json_ld_title = ''
            json_ld_date = ''
            
            try:
                json_scripts = soup.find_all('script', type='application/ld+json')
                for script in json_scripts:
                    try:
                        json_data = json.loads(script.string or '')
                        
                        if isinstance(json_data, list):
                            json_data = json_data[0] if json_data else {}
                        
                        if json_data.get('@type') == 'NewsArticle':
                            article_body = json_data.get('articleBody', '')
                            if article_body and len(article_body) > 200:
                                json_ld_content = article_body
                                json_ld_title = json_data.get('headline', '')
                                json_ld_date = (json_data.get('datePublished') or 
                                              json_data.get('dateCreated') or 
                                              json_data.get('dateModified', ''))
                                break
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                print(f"JSON-LD parsing error: {e}")
            
            # Enhanced title extraction
            title_text = ''
            if json_ld_title:
                title_text = json_ld_title
            else:
                # Try multiple title extraction methods
                title_selectors = [
                    'h1', 'meta[property="og:title"]', 'title',
                    '.article-title', '.post-title', '.entry-title'
                ]
                for selector in title_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        if selector.startswith('meta'):
                            title_text = elem.get('content', '')
                        else:
                            title_text = elem.get_text(strip=True)
                        if title_text and len(title_text) > 10:
                            break
            
            # Use JSON-LD content if available
            if len(json_ld_content) > 200:
                content = json_ld_content
                content_found = True
            else:
                # Enhanced content selectors
                content_selectors = [
                    'div.story-body', 'div.article-body', 'div.content',
                    'div.field-name-body', 'section.article-body',
                    'div.entry-content', 'article .content', 'main article',
                    '[class*="article-content"]', '[class*="story-content"]',
                    'article'
                ]
                
                for selector in content_selectors:
                    content_div = soup.select_one(selector)
                    if content_div:
                        # Extract text content
                        content = content_div.get_text(separator='\n', strip=True)
                        
                        # Filter out subscription notices and navigation
                        unwanted_phrases = [
                            'Your digital subscription',
                            'Access unlimited content',
                            "Today's Paper",
                            'Subscribe now',
                            'Sign up',
                            'Follow us',
                            'Share this',
                            'Related articles'
                        ]
                        
                        for phrase in unwanted_phrases:
                            content = content.replace(phrase, '')
                        
                        # Clean up extra whitespace
                        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
                        
                        if len(content) > 100:
                            content_found = True
                            break
            
            # Enhanced date extraction
            date_text = ''
            if json_ld_date:
                date_text = json_ld_date
            else:
                date_selectors = [
                    'meta[property="article:published_time"]',
                    'meta[name="date"]',
                    'time[datetime]',
                    '.published-date',
                    '.article-date',
                    '.date'
                ]
                for selector in date_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        if selector.startswith('meta'):
                            date_text = elem.get('content', '')
                        elif elem.name == 'time':
                            date_text = elem.get('datetime', '') or elem.get_text(strip=True)
                        else:
                            date_text = elem.get_text(strip=True)
                        if date_text:
                            break
            
            # Create article result
            article_result = {
                'url': url,
                'title': title_text or f'Article from {url}',
                'content': content if content_found else 'Content extraction failed',
                'content_length': len(content) if content_found else 0,
                'date': date_text,
                'scraped_at': datetime.now().isoformat(),
                'success': content_found
            }
            
            results.append(article_result)
            if content_found:
                scraped_count += 1
                
        except requests.RequestException as e:
            # Network/HTTP errors
            results.append({
                'url': url,
                'title': f'Error accessing {url}',
                'content': f'Network error: {str(e)}',
                'content_length': 0,
                'date': '',
                'scraped_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
        except Exception as e:
            # Other errors
            results.append({
                'url': url,
                'title': f'Error processing {url}',
                'content': f'Processing error: {str(e)}',
                'content_length': 0,
                'date': '',
                'scraped_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
    
    return {
        'articles': results,
        'scraped': scraped_count,
        'total': len(urls),
        'timestamp': datetime.now().isoformat()
    }