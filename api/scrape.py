# api/scrape.py
from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            urls = data.get('urls', [])
            query = data.get('query', '')
            
            if not urls:
                self.send_error_response(400, 'No URLs provided')
                return
            
            articles = []
            for i, url in enumerate(urls[:10]):  # Limit to 10 for serverless timeout
                article_data = self.extract_article_data(url, query)
                if article_data:
                    article_data['id'] = i + 1
                    articles.append(article_data)
                time.sleep(1)  # Rate limiting
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'query': query,
                'scraped': len(articles),
                'articles': articles
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def extract_article_data(self, article_url, search_term=""):
        """Extract article data"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(article_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.text.strip()
            
            # Extract date
            date = None
            time_elem = soup.find('time')
            if time_elem:
                date = time_elem.get('datetime', time_elem.text.strip())
            
            # Extract content
            content = ""
            content_selectors = [
                'div.story-content',
                'div.article-content',
                'article',
                'div[itemprop="articleBody"]'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    if paragraphs:
                        content = '\n\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
                        break
            
            if not content:
                all_paragraphs = soup.find_all('p')
                article_paragraphs = []
                for p in all_paragraphs:
                    text = p.text.strip()
                    if text and len(text) > 50:
                        article_paragraphs.append(text)
                if article_paragraphs:
                    content = '\n\n'.join(article_paragraphs)
            
            # Clean the content
            content = self.clean_article_content(content)
            
            if not title or not content:
                return None
            
            return {
                'url': article_url,
                'title': title,
                'date': date,
                'content': content,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return None
    
    def clean_article_content(self, content):
        """Clean article content"""
        if not content:
            return ""
        
        # Deep clean text
        content = content.replace('\\n', '\n').replace('\\r', '').replace('\\t', ' ')
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        content = content.replace('\\"', '"').replace("\\'", "'")
        content = content.replace('"', '"').replace('"', '"')
        content = content.replace(''', "'").replace(''', "'")
        
        # Remove non-printable characters
        content = ''.join(char for char in content if char.isprintable() or char in '\n\t')
        
        # Clean up whitespace
        content = re.sub(r' +', ' ', content)
        content = re.sub(r'\n\s*\n+', '\n\n', content)
        
        # Remove subscription headers
        if 'Your digital subscription' in content:
            for start_phrase in ['A ', 'The ', 'An ', 'Local ', 'Residents']:
                article_start = content.find(start_phrase)
                if article_start > 50:
                    content = content[article_start:]
                    break
        
        # Split into paragraphs and clean
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        cleaned_paragraphs = []
        
        # End markers and skip phrases
        end_markers = [
            'today\'s top stories',
            'grab a quick bite',
            'catch up on the news',
            'get the editor\'s insights',
            'your essential national news',
            'digital replica',
            'crosswords, sudoku'
        ]
        
        skip_phrases = [
            'your digital subscription',
            'access unlimited content',
            'login or signup to continue'
        ]
        
        for para in paragraphs:
            if not para or len(para) < 20:
                continue
            
            para_lower = para.lower()
            
            # Check for end markers
            if any(marker in para_lower for marker in end_markers):
                break
            
            # Check for skip phrases
            if any(skip in para_lower for skip in skip_phrases):
                continue
            
            cleaned_paragraphs.append(para)
        
        return '\n\n'.join(cleaned_paragraphs).strip()
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
