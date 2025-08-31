#!/usr/bin/env python3
"""
Optimized Search API for Newspaper Scraper
Enhanced based on performance testing results - Strategy 2 (Category Scraping) prioritized
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, unquote
import re
import time
import random

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_random_user_agent(self):
        """Get a random user agent for requests to avoid blocking."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
        ]
        return random.choice(user_agents)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '')
            sources = data.get('sources', [])
            max_results = data.get('max_results', 20)
            
            print(f"🔍 Search request: '{query}' from sources: {sources}")
            
            if not query or not sources:
                self.send_error_response(400, "Missing query or sources")
                return
            
            all_articles = []
            
            # Process each requested source
            for source in sources:
                if source == 'illawarra_mercury':
                    articles = self.search_illawarra_mercury_optimized(query, max_results)
                elif source == 'abc_news':
                    articles = self.search_abc_news(query, max_results)
                elif source == 'the_guardian':
                    articles = self.search_the_guardian(query, max_results)
                else:
                    print(f"❌ Unknown source: {source}")
                    continue
                
                all_articles.extend(articles)
            
            # Remove duplicates and prepare response
            unique_articles = []
            seen_urls = set()
            for article in all_articles:
                if article['url'] not in seen_urls:
                    unique_articles.append(article)
                    seen_urls.add(article['url'])
            
            response_data = {
                'query': query,
                'total_results': len(unique_articles),
                'articles': unique_articles
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
            print(f"✅ Returning {len(unique_articles)} articles")
            
        except Exception as e:
            print(f"❌ Request processing error: {e}")
            self.send_error_response(500, f"Internal server error: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def search_illawarra_mercury_optimized(self, query, max_results=20):
        """
        OPTIMIZED SEARCH - Based on performance testing results
        Strategy 2 (Category Scraping) prioritized as it's the only working approach
        """
        articles = []
        seen_urls = set()

        print(f"🎯 OPTIMIZED SEARCH: Starting enhanced category scraping for '{query}'...")
        
        try:
            # ENHANCED CATEGORY LIST (expanded based on discovery - 14 working categories)
            categories = [
                "https://www.illawarramercury.com.au/",  # Homepage - base coverage
                "https://www.illawarramercury.com.au/sport/",  # 218 articles - highest content
                "https://www.illawarramercury.com.au/entertainment/",  # 155 articles - major section
                "https://www.illawarramercury.com.au/news/",  # 125 articles - main news
                "https://www.illawarramercury.com.au/lifestyle/",  # 107 articles - lifestyle content
                "https://www.illawarramercury.com.au/news/business/",  # 80 articles - business news
                "https://www.illawarramercury.com.au/news/environment/",  # 80 articles - environment
                "https://www.illawarramercury.com.au/news/local-news/",  # 78 articles - local coverage
                "https://www.illawarramercury.com.au/sport/basketball/",  # 60 articles - sports subsection
                "https://www.illawarramercury.com.au/news/education/",  # 58 articles - education
                "https://www.illawarramercury.com.au/news/health/",  # 56 articles - health
                "https://www.illawarramercury.com.au/news/politics/",  # 40 articles - politics
                "https://www.illawarramercury.com.au/sport/cricket/",  # 37 articles - cricket
                "https://www.illawarramercury.com.au/community/",  # 27 articles - community
            ]
            
            all_story_urls = []
            for category_url in categories:
                try:
                    headers = {
                        'User-Agent': self.get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive'
                    }
                    
                    resp = requests.get(category_url, headers=headers, timeout=12)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.content, 'lxml')
                    
                    category_count = 0
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href:
                            full_url = urljoin(category_url, href)
                            clean_url = full_url.split('#')[0].split('?')[0]
                            if clean_url not in all_story_urls:
                                all_story_urls.append(clean_url)
                                category_count += 1
                
                    print(f"  ✓ {category_url.split('/')[-2] or 'homepage'}: {category_count} articles")
                
                except Exception as e:
                    print(f"  ✗ Failed to scrape {category_url}: {e}")
                    continue
            
            print(f"📊 Total articles collected: {len(all_story_urls)}")
            
            # ENHANCED SCORING ALGORITHM (optimized based on test results)
            query_lower = query.lower()
            query_words = [word.lower() for word in query.split() if len(word) > 2]
            
            # Enhanced variations for better matching
            query_variations = [
                query_lower,
                query_lower.replace(' ', '-'),
                query_lower.replace(' ', '_'),
                query_lower.replace('council', 'city-council'),
                query_lower.replace('council', 'city_council'),
                'shellharbour-city-council' if 'shellharbour' in query_lower else None,
                'shell-harbour' if 'shellharbour' in query_lower else None,
                'shell cove' if 'shellharbour' in query_lower else None,  # Related area
                'shellcove' if 'shellharbour' in query_lower else None,
            ]
            query_variations = [v for v in query_variations if v]
            
            print(f"🔍 Query variations: {query_variations}")
            
            # Score URLs with enhanced algorithm
            url_scores = []
            for story_url in all_story_urls:
                url_text = story_url.lower()
                score = 0
                
                # HIGHEST PRIORITY: Exact phrase matches (proven effective in testing)
                for variation in query_variations:
                    if variation in url_text:
                        score += 50  # Increased based on success rate
                        break
                
                # HIGH PRIORITY: Individual words in URL
                words_found = 0
                for word in query_words:
                    if word in url_text:
                        score += 15  # Increased from original 10
                        words_found += 1
                        # Extra bonus for words in story slug (after /story/)
                        if '/story/' in url_text and word in url_text.split('/story/')[-1]:
                            score += 10  # Increased from original 5
                
                # SPECIAL HANDLING: Shellharbour variations (important for local news)
                if 'shellharbour' in query_lower:
                    shellharbour_variants = ['shellharbour', 'shell-harbour', 'shell-cove', 'shellcove']
                    for variant in shellharbour_variants:
                        if variant in url_text:
                            score += 12
                
                # COMPOUND TERM BONUS (multiple words found together)
                if len(query_words) > 1 and words_found > 1:
                    score += words_found * 5  # Increased multiplier
                
                # LOCATION + ORGANIZATION COMBINATIONS
                if len(query_words) >= 2:
                    story_part = url_text.split('/story/')[-1] if '/story/' in url_text else url_text
                    if any(word in story_part for word in query_words):
                        score += 15
                
                if score > 0:
                    url_scores.append((score, story_url))
            
            # Sort by relevance and get top results
            url_scores.sort(reverse=True, key=lambda x: x[0])
            
            print(f"🏆 Top scoring URLs:")
            for i, (score, url) in enumerate(url_scores[:5], 1):
                url_slug = url.split('/')[-1] if url.split('/')[-1] else url.split('/')[-2]
                print(f"  {i}. Score {score}: {url_slug}")
            
            # Convert top URLs to article objects
            for score, url in url_scores[:max_results]:
                if url not in seen_urls:
                    try:
                        # Fetch article details
                        article_headers = {
                            'User-Agent': self.get_random_user_agent(),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Connection': 'keep-alive'
                        }
                        
                        resp = requests.get(url, headers=article_headers, timeout=10)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.content, 'lxml')
                            
                            # Extract title
                            title_elem = soup.find('h1')
                            title = title_elem.get_text().strip() if title_elem else "No title"
                            
                            # Extract description
                            desc_elem = soup.find('meta', {'name': 'description'})
                            description = desc_elem.get('content', '').strip() if desc_elem else ""
                            
                            # If no meta description, try first paragraph
                            if not description:
                                first_p = soup.find('p')
                                description = first_p.get_text().strip()[:200] + "..." if first_p else ""
                            
                            article = {
                                'title': title,
                                'url': url,
                                'description': description,
                                'source': 'illawarra_mercury',
                                'relevance_score': score
                            }
                            
                            articles.append(article)
                            seen_urls.add(url)
                            
                            # Small delay to be respectful
                            time.sleep(0.3)
                            
                    except Exception as e:
                        print(f"  ⚠️ Failed to fetch details for {url}: {e}")
                        continue
            
            print(f"✅ Successfully processed {len(articles)} articles")
            
            # FALLBACK: Content analysis if URL scoring found few results
            if len(articles) < 3 and len(all_story_urls) > 20:
                print(f"🔄 Low URL match count ({len(articles)}), trying enhanced content analysis...")
                try:
                    fallback_articles = self._content_analysis_fallback(query, all_story_urls, seen_urls, max_results - len(articles))
                    articles.extend(fallback_articles)
                except AttributeError:
                    # Fallback method not available, skip enhanced content analysis
                    print("⚠️ Enhanced content analysis not available, continuing with URL matches")
                    pass
            
            return articles
            
        except Exception as e:
            print(f"❌ Optimized search failed: {e}")
            return []

    def _content_analysis_fallback(self, query, all_story_urls, seen_urls, remaining_slots):
        """Enhanced content analysis as fallback when URL matching finds few results"""
        articles = []
        query_lower = query.lower()
        query_words = [word.lower() for word in query.split() if len(word) > 2]
        
        # Enhanced phrase variations for content matching
        phrase_variations = [
            query_lower,
            query_lower.replace(' ', '-'),
            'shellharbour city council' if 'shellharbour' in query_lower else None,
            'shell harbour council' if 'shellharbour' in query_lower else None,
        ]
        phrase_variations = [v for v in phrase_variations if v]
        
        print(f"🔍 Content analysis for phrases: {phrase_variations}")
        
        title_matches = []
        # Check more articles for content matches
        articles_to_check = min(100, len(all_story_urls))  # Increased from 80
        
        for story_url in all_story_urls[:articles_to_check]:
            if story_url in seen_urls:
                continue
                
            try:
                headers = {
                    'User-Agent': self.get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Connection': 'keep-alive'
                }
                
                resp = requests.get(story_url, headers=headers, timeout=8)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')
                    
                    # Get title and meta description
                    title_text = ""
                    title_elem = soup.find('h1')
                    if title_elem:
                        title_text = title_elem.get_text().lower()
                    
                    meta_desc = ""
                    meta_elem = soup.find('meta', {'name': 'description'})
                    if meta_elem:
                        meta_desc = meta_elem.get('content', '').lower()
                    
                    # Also check first paragraph
                    first_p = ""
                    first_p_elem = soup.find('p')
                    if first_p_elem:
                        first_p = first_p_elem.get_text().lower()[:300]
                    
                    combined_text = f"{title_text} {meta_desc} {first_p}"
                    content_score = 0
                    
                    # Check for exact phrase matches (highest value)
                    for variation in phrase_variations:
                        if variation in combined_text:
                            content_score += 25  # Increased from 18
                            break
                    
                    # Check individual words
                    words_found = 0
                    for word in query_words:
                        if word in combined_text:
                            content_score += 8  # Increased from 5
                            words_found += 1
                            # Extra points if word is in title
                            if word in title_text:
                                content_score += 5  # Increased from 3
                    
                    # Special handling for Shellharbour + Council combinations
                    if 'shellharbour' in query.lower():
                        shellharbour_variants = ['shellharbour', 'shell harbour', 'shell-harbour']
                        council_variants = ['council', 'city council', 'city-council']
                        
                        has_location = any(variant in combined_text for variant in shellharbour_variants)
                        has_council = any(variant in combined_text for variant in council_variants)
                        
                        if has_location and has_council:
                            content_score += 20  # Increased from 15
                        elif has_location:
                            content_score += 10  # Increased from 8
                    
                    # Bonus for multiple words found
                    if len(query_words) > 1 and words_found > 1:
                        content_score += words_found * 4  # Increased multiplier
                    
                    if content_score > 0:
                        title_matches.append((content_score, story_url, title_elem.get_text().strip() if title_elem else "No title"))
                        if len(title_matches) >= remaining_slots:
                            break
            
            except Exception:
                continue
            
            time.sleep(0.3)  # Be respectful
        
        # Sort and convert to articles
        title_matches.sort(reverse=True, key=lambda x: x[0])
        
        print(f"📊 Content analysis results:")
        for i, (score, url, title) in enumerate(title_matches[:5], 1):
            print(f"  {i}. Score {score}: {title[:50]}...")
        
        for score, url, title in title_matches[:remaining_slots]:
            try:
                # Get description
                resp = requests.get(url, headers={'User-Agent': self.get_random_user_agent()}, timeout=8)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')
                    desc_elem = soup.find('meta', {'name': 'description'})
                    description = desc_elem.get('content', '').strip() if desc_elem else ""
                    
                    article = {
                        'title': title,
                        'url': url,
                        'description': description,
                        'source': 'illawarra_mercury',
                        'relevance_score': score
                    }
                    articles.append(article)
                    
            except Exception:
                continue
        
        print(f"✅ Content analysis found {len(articles)} additional articles")
        return articles

    def search_abc_news(self, query, max_results):
        """Search ABC News (kept from original for completeness)"""
        try:
            base_url = "https://www.abc.net.au"
            search_url = f"https://www.abc.net.au/news/search?query={quote_plus(query)}"
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            for result in soup.select('a[data-component="Link"]'):
                href = result.get('href', '')
                if href and '/news/' in href and 'live-updates' not in href:
                    full_url = urljoin(base_url, href)
                    title_elem = result.find(string=True)
                    title = title_elem.strip() if title_elem else "No title"
                    
                    article = {
                        'title': title,
                        'url': full_url,
                        'description': "",
                        'source': 'abc_news'
                    }
                    articles.append(article)
                    if len(articles) >= max_results:
                        break
            return articles
        except Exception as e:
            print(f"Error in ABC News search: {e}")
            return []

    def search_the_guardian(self, query, max_results):
        """Search The Guardian (kept from original for completeness)"""
        try:
            search_url = f"https://www.theguardian.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            for result in soup.select('h3.fc-item__title'):
                link_elem = result.find('a')
                if link_elem:
                    href = link_elem.get('href', '')
                    title = link_elem.get_text().strip()
                    
                    if href and title:
                        article = {
                            'title': title,
                            'url': href,
                            'description': "",
                            'source': 'the_guardian'
                        }
                        articles.append(article)
                        if len(articles) >= max_results:
                            break
            return articles
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
                print(f"Critical error - unable to send any response: {message}")

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Optimized Search API starting on http://localhost:8000")
    print("📊 Based on performance testing - Strategy 2 (Category Scraping) prioritized")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        server.shutdown()
