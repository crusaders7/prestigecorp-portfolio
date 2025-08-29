# api/scrape.py
from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime


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
                    article_data = self.extract_article_data(url)

                    if 'error' not in article_data:
                        results.append(article_data)
                        scraped_count += 1
                    else:
                        results.append(article_data)

                    # Rate limiting - respectful scraping
                    time.sleep(1)

                except Exception as e:
                    print(f"Error processing {url}: {type(e).__name__}: {e}")
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

    def extract_article_data(self, url, search_term=""):
        """Extract article data using provider-specific or generic methods."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            }

            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'lxml')

            if "illawarramercury.com.au" in url:
                return self.extract_illawarra_mercury_data(soup, url)
            else:
                # Generic extraction for other sites
                title = self.extract_title(soup)
                date_str = self.extract_date(soup)
                content = self.extract_content(soup)
                content = self.clean_article_content(content)

                return {
                    'url': url,
                    'title': title,
                    'date': date_str,
                    'content': content,
                    'scraped_at': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error extracting data from {url}: {e}")
            return {'url': url, 'error': str(e)}

    def extract_illawarra_mercury_data(self, soup, url):
        """Extracts article data specifically for Illawarra Mercury"""
        try:
            # Title
            title_elem = soup.find('h1', attrs={'data-testid': 'story-title'})
            title = title_elem.get_text(
                strip=True) if title_elem else self.extract_title(soup)

            # Author
            author_elem = soup.find('a', attrs={'data-testid': 'author-link'})
            author = author_elem.get_text(
                strip=True) if author_elem else 'No author found'

            # Date
            date_str = self.extract_date(soup)

            # Content
            content = ''
            story_body_div = soup.find('div', id='story-body')
            if story_body_div:
                paragraphs = story_body_div.find_all(
                    'p', class_='Paragraph_wrapper__6w7GG')
                content = "\n\n".join([p.get_text(strip=True)
                                      for p in paragraphs])

            if not content:  # Fallback to generic extraction if specific one fails
                content = self.extract_content(soup)

            # Clean content
            content = self.clean_article_content(content)

            return {
                'url': url,
                'title': title,
                'author': author,
                'date': date_str,
                'content': content,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error in extract_illawarra_mercury_data for {url}: {e}")
            # Fallback to generic extraction on specific error
            title = self.extract_title(soup)
            date_str = self.extract_date(soup)
            content = self.extract_content(soup)
            return {
                'url': url,
                'title': title,
                'date': date_str,
                'content': self.clean_article_content(content),
                'scraped_at': datetime.now().isoformat(),
                'extraction_error': str(e)
            }

    def extract_title(self, soup):
        """Extracts title using a series of selectors."""
        title_selectors = ['h1[data-testid="story-title"]',
                           'h1', '.headline', '.story-headline', '.article-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)

        # Fallback to <title> tag
        if soup.title and soup.title.string:
            return soup.title.string

        return 'No title found'

    def extract_content(self, soup):
        """Extract full article content by aggregating all <p> tags from likely containers, or all <p> tags on the page if needed."""
        # List of likely content containers
        content_selectors = [
            'div[data-testid="story-body"]',
            'div.story-body__inner',
            'div.article-body',
            'div[itemprop="articleBody"]',
            'article.article-body',
            'div.main-content',
            'div.story-content',
            'div.content',
            'article',
        ]

        paragraphs = []
        # Aggregate <p> tags from all likely containers
        for selector in content_selectors:
            for container in soup.select(selector):
                # Remove known non-content elements
                for ad_selector in ['.ad-slot', '.related-articles', '.subscription-prompt', 'aside', 'nav', 'footer']:
                    for ad_element in container.select(ad_selector):
                        ad_element.decompose()
                ps = container.find_all('p', recursive=True)
                paragraphs.extend([p.get_text(strip=True) for p in ps if p.get_text(strip=True)])

        # Remove duplicates while preserving order
        seen = set()
        unique_paragraphs = []
        for p in paragraphs:
            if p not in seen:
                unique_paragraphs.append(p)
                seen.add(p)

        content = '\n\n'.join(unique_paragraphs)
        if len(content) > 200:  # More strict check for meaningful content
            return content

        # Fallback: aggregate all <p> tags on the page, excluding those in nav, footer, aside
        all_paragraphs = []
        for p in soup.find_all('p'):
            # Exclude <p> tags inside nav, footer, aside
            parent = p.parent
            skip = False
            while parent is not None:
                if parent.name in ['nav', 'footer', 'aside']:
                    skip = True
                    break
                parent = parent.parent
            if not skip and p.get_text(strip=True):
                all_paragraphs.append(p.get_text(strip=True))
        content = '\n\n'.join(all_paragraphs)
        if len(content) > 200:
            return content

        # Ultimate fallback to meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', 'Could not extract article content.')

        return 'Could not extract article content.'

    def extract_date(self, soup):
        """Extract publication date using multiple methods"""
        # Try time tag first
        date_elem = soup.find('time')
        if date_elem:
            date_str = date_elem.get(
                'datetime') or date_elem.get_text(strip=True)
            if date_str:
                return date_str

        # Try meta tags
        meta_selectors = [
            'meta[name="pubdate"]',
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'meta[property="article:modified_time"]'
        ]

        for selector in meta_selectors:
            meta_elem = soup.select_one(selector)
            if meta_elem:
                date_str = meta_elem.get('content')
                if date_str:
                    return date_str

        return ''

    def clean_article_content(self, content):
        """Multi-stage content cleaning"""
        if not content:
            return content

        # Unicode normalization
        content = content.replace('"', '"').replace('"', '"')
        content = content.replace(''', "'").replace(''', "'")

        # Remove subscription prompts and ads
        skip_phrases = [
            'your digital subscription',
            'access unlimited content',
            'login or signup to continue',
            'subscribe now',
            'premium content',
            'read more',
            'advertisement'
        ]

        # Smart paragraph filtering
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        cleaned_paragraphs = []

        for para in paragraphs:
            if len(para) < 20:  # Skip very short paragraphs
                continue
            if any(skip in para.lower() for skip in skip_phrases):
                continue
            cleaned_paragraphs.append(para)

        return '\n\n'.join(cleaned_paragraphs)
