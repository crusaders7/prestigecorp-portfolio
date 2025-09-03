import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def handler(request, response):
    """Vercel serverless function handler for article scraping"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response.status_code = 200
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
        return ''
    
    # Only allow POST requests
    if request.method != 'POST':
        response.status_code = 405
        response.headers.update({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
        return json.dumps({
            'error': 'Method not allowed. Use POST.',
            'status': 405,
            'timestamp': datetime.now().isoformat()
        })
    
    try:
        # Parse request data
        if hasattr(request, 'get_json'):
            data = request.get_json() or {}
        else:
            # Handle raw request body
            if hasattr(request, 'body'):
                body = request.body
            elif hasattr(request, 'data'):
                body = request.data
            else:
                body = b'{}'
            
            if isinstance(body, str):
                body = body.encode('utf-8')
            
            try:
                data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {}
        
        urls = data.get('urls', [])
        if not urls or not isinstance(urls, list):
            response.status_code = 400
            response.headers.update({
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            })
            return json.dumps({
                'error': 'No URLs provided or URLs not in list format',
                'status': 400,
                'timestamp': datetime.now().isoformat()
            })
        
        # Scrape articles
        results = scrape_articles(urls)
        
        # Send response
        response.status_code = 200
        response.headers.update({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
        
        return json.dumps(results, ensure_ascii=False)
        
    except Exception as e:
        response.status_code = 500
        response.headers.update({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
        
        return json.dumps({
            'error': f'Internal server error: {str(e)}',
            'status': 500,
            'timestamp': datetime.now().isoformat()
        })


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
            date_text = json_ld_date if json_ld_date else ''
            if not date_text:
                date_selectors = [
                    'meta[property="article:published_time"]',
                    'meta[name="date"]',
                    'meta[name="publish-date"]',
                    'time[datetime]',
                    '.date', '.publish-date', '.article-date'
                ]
                
                for selector in date_selectors:
                    date_elem = soup.select_one(selector)
                    if date_elem:
                        if selector.startswith('meta'):
                            date_text = date_elem.get('content', '')
                        elif selector == 'time[datetime]':
                            date_text = date_elem.get('datetime', '')
                        else:
                            date_text = date_elem.get_text(strip=True)
                        if date_text:
                            break
            
            if content_found and len(content) > 50:
                article_data = {
                    'url': url,
                    'title': title_text or f'Article {i+1}',
                    'content': content,
                    'content_length': len(content),
                    'date': date_text,
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'web_scraping'
                }
                results.append(article_data)
                scraped_count += 1
            else:
                # Add error entry for failed scraping
                results.append({
                    'url': url,
                    'error': 'Could not extract sufficient content',
                    'scraped_at': datetime.now().isoformat()
                })
                
        except requests.RequestException as e:
            results.append({
                'url': url,
                'error': f'Request failed: {str(e)}',
                'scraped_at': datetime.now().isoformat()
            })
        except Exception as e:
            results.append({
                'url': url,
                'error': f'Scraping error: {str(e)}',
                'scraped_at': datetime.now().isoformat()
            })
    
    # Separate successful articles from errors
    articles = [r for r in results if 'content' in r]
    errors = [r for r in results if 'error' in r]
    
    return {
        'scraped': scraped_count,
        'total_requested': len(urls),
        'articles': articles,
        'errors': errors,
        'timestamp': datetime.now().isoformat()
    }

                        content = ''
                        content_found = False
                        
                        # Try each selector until we find substantial content
                        for selector in content_selectors:
                            try:
                                content_div = soup.select_one(selector)
                                if content_div:
                                    # Method 1: Extract text from paragraphs only
                                    paragraphs = content_div.find_all('p')
                                    paragraph_texts = []
                                    
                                    for p in paragraphs:
                                        text = p.get_text(strip=True)
                                        # Skip subscription notices, ads, and navigation
                                        if (text and len(text) > 50 and 
                                            not any(skip_word in text.lower() for skip_word in [
                                                'your digital subscription', 'access unlimited content',
                                                'today\'s paper', 'subscribe', 'subscription', 'sign up',
                                                'newsletter', 'follow us', 'share this', 'read more',
                                                'click here', 'advertisement', 'sponsored', 'related articles',
                                                'more stories', 'breaking news', 'latest news', 'trending'
                                            ])):
                                            paragraph_texts.append(text)
                                    
                                    if paragraph_texts:
                                        content = ' '.join(paragraph_texts)
                                        
                                    # Method 2: If paragraphs don't give enough, try all text
                                    if len(content) < 200:
                                        # Remove unwanted elements first
                                        for unwanted in content_div.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
                                            unwanted.decompose()
                                        
                                        # Remove subscription boxes
                                        for sub_box in content_div.find_all(attrs={'class': lambda x: x and any(word in ' '.join(x).lower() for word in ['subscribe', 'subscription', 'paywall', 'premium'])}):
                                            sub_box.decompose()
                                        
                                        full_text = content_div.get_text(separator=' ', strip=True)
                                        
                                        # Clean up the text
                                        lines = full_text.split('.')
                                        clean_lines = []
                                        
                                        for line in lines:
                                            line = line.strip()
                                            if (len(line) > 30 and 
                                                not any(skip in line.lower() for skip in [
                                                    'digital subscription', 'unlimited content', 'today\'s paper',
                                                    'subscribe', 'newsletter', 'breaking news', 'latest news'
                                                ])):
                                                clean_lines.append(line)
                                        
                                        if clean_lines and len(' '.join(clean_lines)) > len(content):
                                            content = '. '.join(clean_lines)
                                    
                                    # If we found substantial content (more than 300 chars), use it
                                    if len(content) > 300:
                                        print(f"Found content using selector: {selector} ({len(content)} chars)")
                                        content_found = True
                                        break
                                    elif len(content) > 100:
                                        print(f"Found partial content using selector: {selector} ({len(content)} chars)")
                                        # Continue looking but keep this as backup
                                        
                            except Exception as selector_error:
                                print(f"Error with selector {selector}: {selector_error}")
                                continue

                        # Enhanced fallback methods if no content found
                        if not content_found or len(content) < 200:
                            print("Using enhanced fallback content extraction methods")
                            
                            # Fallback 1: Look for any div with substantial paragraph content
                            all_divs = soup.find_all('div')
                            best_content = ''
                            
                            for div in all_divs:
                                div_paragraphs = div.find_all('p', recursive=False)
                                if len(div_paragraphs) >= 3:  # At least 3 paragraphs
                                    div_text = ' '.join([p.get_text(strip=True) for p in div_paragraphs[:8]])
                                    # Skip if it contains subscription text
                                    if (len(div_text) > 500 and 
                                        'digital subscription' not in div_text.lower() and
                                        'unlimited content' not in div_text.lower()):
                                        if len(div_text) > len(best_content):
                                            best_content = div_text
                            
                            if len(best_content) > len(content):
                                content = best_content
                                print(f"Used div fallback: {len(content)} chars")
                            
                            # Fallback 2: Get all paragraphs from the entire page (more selective)
                            if len(content) < 200:
                                all_paragraphs = soup.find_all('p')
                                good_paragraphs = []
                                
                                for p in all_paragraphs:
                                    text = p.get_text(strip=True)
                                    if (len(text) > 80 and  # Longer minimum
                                        not any(skip in text.lower() for skip in [
                                            'cookie', 'subscribe', 'newsletter', 'advertisement',
                                            'digital subscription', 'unlimited content', 'today\'s paper',
                                            'follow us', 'share this', 'latest news', 'breaking news'
                                        ])):
                                        good_paragraphs.append(text)
                                    if len(good_paragraphs) >= 6:  # Limit to avoid too much content
                                        break
                                
                                if good_paragraphs:
                                    fallback_content = ' '.join(good_paragraphs)
                                    if len(fallback_content) > len(content):
                                        content = fallback_content
                                        print(f"Used paragraph fallback: {len(content)} chars")
                            
                            # Fallback 3: Meta description as last resort
                            if len(content) < 100:
                                meta_desc = soup.find('meta', attrs={'name': 'description'})
                                if meta_desc:
                                    content = meta_desc.get('content', '')
                                    print(f"Used meta description: {len(content)} chars")

                    # Ensure content is a string
                    if not isinstance(content, str):
                        content = str(content)

                    # Enhanced date extraction
                    date_str = ''
                    
                    # PRIORITY 1: Use JSON-LD date if available
                    if json_ld_date:
                        date_str = json_ld_date
                        print(f"Using JSON-LD date: {date_str}")
                    else:
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
