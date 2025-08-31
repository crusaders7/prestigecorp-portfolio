from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, unquote
import time
import re
import random


class handler(BaseHTTPRequestHandler):
    def get_random_user_agent(self):
        """Return a random user agent to avoid blocking"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/118.0.2088.46'
        ]
        return random.choice(user_agents)
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
        
        # Strategy 1: Use site's own search function (most comprehensive)
        try:
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}"
            print(f"Trying site search: {search_url}")
            
            resp = requests.get(search_url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'lxml')
            
            # Look for search results - try multiple selectors
            search_results = []
            
            # Common selectors for search results
            for selector in [
                'article a[href*="/story/"]',
                '.search-result a[href*="/story/"]',
                '.story-block a[href*="/story/"]',
                'h3 a[href*="/story/"]',
                'h2 a[href*="/story/"]',
                'a[href*="/story/"]'
            ]:
                links = soup.select(selector)
                if links:
                    print(f"Found {len(links)} links with selector: {selector}")
                    for link in links:
                        href = link.get('href', '')
                        if '/story/' in href:
                            full_url = urljoin("https://www.illawarramercury.com.au", href)
                            clean_url = full_url.split('#')[0].split('?')[0]
                            if clean_url not in seen_urls:
                                search_results.append(clean_url)
                                seen_urls.add(clean_url)
                    break  # Use first working selector
            
            print(f"Site search found {len(search_results)} article URLs")
            
            if search_results:
                # Take the first batch of results but don't return yet - continue to Strategy 2
                relevant_urls = search_results[:max_results]
                urls.extend(relevant_urls)
                print(f"Strategy 1 (site search) collected {len(relevant_urls)} articles")
        
        except Exception as e:
            print(f"Site search failed: {e}")
        
        # Strategy 2: OPTIMIZED CATEGORY SCRAPING (Top performing categories prioritized)
        # Based on comprehensive discovery - focus on highest-value categories first
        print(f"Starting optimized category scraping with priority categories...")
        try:
            # TIER 1: HIGHEST PRIORITY (100+ articles) - Best ROI for local content
            tier1_categories = [
                "https://www.illawarramercury.com.au/",  # Main page - 431 stories
                "https://www.illawarramercury.com.au/sport/",  # 218 stories - highest category
                "https://www.illawarramercury.com.au/entertainment/",  # 155 stories
                "https://www.illawarramercury.com.au/news/",  # 125 stories
                "https://www.illawarramercury.com.au/news/cost-of-living/",  # 124 stories - community interest
                "https://www.illawarramercury.com.au/lifestyle/",  # 107 stories
            ]
            
            # TIER 2: HIGH PRIORITY (50-99 articles) - Strong content coverage
            tier2_categories = [
                "https://www.illawarramercury.com.au/sport/national-sport/",  # 96 stories
                "https://www.illawarramercury.com.au/news/car-expert/",  # 83 stories
                "https://www.illawarramercury.com.au/lifestyle/food-drink/",  # 83 stories
                "https://www.illawarramercury.com.au/news/business/",  # 80 stories - council business
                "https://www.illawarramercury.com.au/news/environment/",  # 80 stories - council environment
                "https://www.illawarramercury.com.au/entertainment/technology/",  # 80 stories
                "https://www.illawarramercury.com.au/entertainment/gaming/",  # 79 stories
                "https://www.illawarramercury.com.au/news/local-news/your-news/",  # 78 stories - LOCAL focus
                "https://www.illawarramercury.com.au/news/local-news/",  # 78 stories - LOCAL focus
                "https://www.illawarramercury.com.au/lifestyle/home-garden/",  # 76 stories
                "https://www.illawarramercury.com.au/news/local-news/babies-weddings-obituaries/",  # 76 stories
                "https://www.illawarramercury.com.au/lifestyle/parenting/",  # 75 stories
                "https://www.illawarramercury.com.au/news/local-news/history/",  # 74 stories
                "https://www.illawarramercury.com.au/lifestyle/money/",  # 73 stories - rates/costs
                "https://www.illawarramercury.com.au/sport/local-league/",  # 72 stories - local sports
                "https://www.illawarramercury.com.au/sport/hawks-nest/",  # 72 stories
                "https://www.illawarramercury.com.au/entertainment/movies/",  # 70 stories
                "https://www.illawarramercury.com.au/sport/local-sport/",  # 70 stories - local sports
                "https://www.illawarramercury.com.au/sport/dragons-den/",  # 68 stories
                "https://www.illawarramercury.com.au/news/court-crime/",  # 66 stories - local issues
                "https://www.illawarramercury.com.au/lifestyle/pets-animals/",  # 66 stories
                "https://www.illawarramercury.com.au/lifestyle/health-wellbeing/",  # 63 stories
                "https://www.illawarramercury.com.au/sport/junior-sport/",  # 62 stories
                "https://www.illawarramercury.com.au/entertainment/books/",  # 61 stories
                "https://www.illawarramercury.com.au/news/education/",  # 58 stories - schools/council
                "https://www.illawarramercury.com.au/sport/toyota-hub/",  # 58 stories
                "https://www.illawarramercury.com.au/news/health/",  # 56 stories - public health
                "https://www.illawarramercury.com.au/news/national/",  # 54 stories
                "https://www.illawarramercury.com.au/entertainment/arts-and-theatre/",  # 51 stories
                "https://www.illawarramercury.com.au/lifestyle/food-drink/recipes/",  # 50 stories
                "https://www.illawarramercury.com.au/entertainment/music/",  # 50 stories
            ]
            
            # TIER 3: COMPREHENSIVE COVERAGE (20-49 articles) - Complete discovery results
            tier3_categories = [
                "https://www.illawarramercury.com.au/news/weather/",  # 46 stories
                "https://www.illawarramercury.com.au/sport/a-league/",  # 46 stories
                "https://www.illawarramercury.com.au/lifestyle/shopping/",  # 46 stories
                "https://www.illawarramercury.com.au/news/nsw/",  # 44 stories
                "https://www.illawarramercury.com.au/entertainment/tv-and-streaming/",  # 44 stories
                "https://www.illawarramercury.com.au/sport/world/",  # 42 stories
                "https://www.illawarramercury.com.au/news/how-many-more/",  # 41 stories
                "https://www.illawarramercury.com.au/news/politics/",  # 40 stories - GOVERNMENT
                "https://www.illawarramercury.com.au/news/world/",  # 40 stories
                "https://www.illawarramercury.com.au/sport/cricket/",  # 37 stories
                "https://www.illawarramercury.com.au/sport/afl/",  # 36 stories
                "https://www.illawarramercury.com.au/sport/local-afl/",  # 36 stories
                "https://www.illawarramercury.com.au/sport/nrl/",  # 36 stories
                "https://www.illawarramercury.com.au/lifestyle/celebrity/",  # 36 stories
                "https://www.illawarramercury.com.au/lifestyle/celebrity/royals/",  # 36 stories
                "https://www.illawarramercury.com.au/lifestyle/fashion/",  # 36 stories
                "https://www.illawarramercury.com.au/lifestyle/beauty/",  # 35 stories
                "https://www.illawarramercury.com.au/sport/local-racing/",  # 28 stories
                "https://www.illawarramercury.com.au/community/",  # 27 stories - community events
                "https://www.illawarramercury.com.au/lifestyle/relationships/",  # 22 stories
                "https://www.illawarramercury.com.au/lifestyle/relationships/dating/",  # 20 stories
                # SPECIALIZED TIER (1-19 stories) - Niche but valuable content
                "https://www.illawarramercury.com.au/lifestyle/food-drink/restaurants/",  # 8 stories
                "https://www.illawarramercury.com.au/news/property/",  # 6 stories
                "https://www.illawarramercury.com.au/entertainment/tv-streaming/tv-guide/",  # 6 stories
            ]
            
            # Start with priority categories
            category_urls = tier1_categories.copy()
            
            all_story_urls = []
            
            for category_url in category_urls:
                try:
                    # Use a fresh user agent for each category
                    category_headers = {
                        'User-Agent': self.get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive'
                    }
                    resp = requests.get(category_url, headers=category_headers, timeout=12)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.content, 'lxml')
                    
                    # Find all story links with more comprehensive search
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href:
                            full_url = urljoin("https://www.illawarramercury.com.au", href)
                            # Remove comments/fragments and query params for clean deduplication
                            clean_url = full_url.split('#')[0].split('?')[0]
                            if clean_url not in all_story_urls:
                                all_story_urls.append(clean_url)
                
                except Exception as e:
                    print(f"Failed to scrape category {category_url}: {e}")
                    continue
            
            print(f"Found {len(all_story_urls)} total articles from priority categories")
            
            # DYNAMIC EXPANSION: Add more categories if initial results are limited
            relevant_found = 0
            query_lower = query.lower()
            query_words = [word.lower() for word in query.split() if len(word) > 2]
            
            # Quick relevance check on collected URLs
            for story_url in all_story_urls[:50]:  # Check first 50 for speed
                url_text = story_url.lower()
                if any(word in url_text for word in query_words) or query_lower in url_text:
                    relevant_found += 1
            
            print(f"Quick scan found {relevant_found} potentially relevant articles")
            
            # If we found fewer than 3 relevant URLs, add tier 2 categories
            if relevant_found < 3:
                print("Adding tier 2 categories for broader coverage...")
                category_urls.extend(tier2_categories)
                
                # Scan tier 2 categories
                for category_url in tier2_categories:
                    try:
                        category_headers = {
                            'User-Agent': self.get_random_user_agent(),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Connection': 'keep-alive'
                        }
                        resp = requests.get(category_url, headers=category_headers, timeout=10)
                        resp.raise_for_status()
                        soup = BeautifulSoup(resp.content, 'lxml')
                        
                        tier2_count = 0
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if '/story/' in href:
                                full_url = urljoin("https://www.illawarramercury.com.au", href)
                                clean_url = full_url.split('#')[0].split('?')[0]
                                if clean_url not in all_story_urls:
                                    all_story_urls.append(clean_url)
                                    tier2_count += 1
                        
                        print(f"  Added {tier2_count} articles from {category_url.split('/')[-2]}")
                    
                    except Exception as e:
                        print(f"  Failed to scrape tier 2 category {category_url}: {e}")
                        continue
                
                print(f"Total articles after tier 2: {len(all_story_urls)}")
            
            # If still limited results, add tier 3 for comprehensive coverage
            if relevant_found < 2 and len(all_story_urls) < 200:
                print("Adding tier 3 categories for comprehensive coverage...")
                category_urls.extend(tier3_categories)
                
                for category_url in tier3_categories:
                    try:
                        category_headers = {
                            'User-Agent': self.get_random_user_agent(),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Connection': 'keep-alive'
                        }
                        resp = requests.get(category_url, headers=category_headers, timeout=10)
                        resp.raise_for_status()
                        soup = BeautifulSoup(resp.content, 'lxml')
                        
                        tier3_count = 0
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if '/story/' in href:
                                full_url = urljoin("https://www.illawarramercury.com.au", href)
                                clean_url = full_url.split('#')[0].split('?')[0]
                                if clean_url not in all_story_urls:
                                    all_story_urls.append(clean_url)
                                    tier3_count += 1
                        
                        print(f"  Added {tier3_count} articles from {category_url.split('/')[-2]}")
                    
                    except Exception:
                        continue
                
                print(f"Final total articles: {len(all_story_urls)}")
            
            print(f"Proceeding with {len(all_story_urls)} articles for relevance analysis...")
            
            # Strategy 1a: URL keyword matching with scoring (enhanced for compound terms)
            # query_lower and query_words already defined above for dynamic expansion
            
            # Create variations for better matching
            query_variations = [
                query_lower,
                query_lower.replace(' ', '-'),
                query_lower.replace(' ', '_'),
                query_lower.replace('council', 'city-council'),
                query_lower.replace('council', 'city_council'),
                'shellharbour-city-council' if 'shellharbour' in query_lower else None,
                'shell-harbour' if 'shellharbour' in query_lower else None
            ]
            query_variations = [v for v in query_variations if v]  # Remove None values
            
            # Score URLs based on relevance
            url_scores = []
            for story_url in all_story_urls:
                url_text = story_url.lower()
                score = 0
                
                # Check for exact phrase matches with variations (highest priority)
                for variation in query_variations:
                    if variation in url_text:
                        score += 30  # Higher bonus for phrase variations
                        break
                
                # Check individual words
                words_found = 0
                for word in query_words:
                    if word in url_text:
                        score += 10
                        words_found += 1
                        # Bonus for word appearing in the story slug (after /story/)
                        if '/story/' in url_text and word in url_text.split('/story/')[-1]:
                            score += 5
                
                # Check for partial word matches (shellharbour vs shell-harbour)
                if 'shellharbour' in query_lower:
                    if 'shell-harbour' in url_text or 'shellharbour' in url_text:
                        score += 8
                
                # Bonus for finding multiple query words (compound terms)
                if len(query_words) > 1 and words_found > 1:
                    score += words_found * 3  # Extra points for multiple matches
                
                # Special handling for location + organization combinations
                if len(query_words) >= 2:
                    # Check for partial matches in story slug
                    story_part = url_text.split('/story/')[-1] if '/story/' in url_text else url_text
                    if any(word in story_part for word in query_words):
                        score += 8
                
                if score > 0:
                    url_scores.append((score, story_url))
            
            # Sort by relevance score and take top results
            url_scores.sort(reverse=True, key=lambda x: x[0])
            relevant_urls = [url for score, url in url_scores[:max_results]]
            
            print(f"Found {len(relevant_urls)} relevant URL matches")
            if url_scores:
                print(f"Top scores: {[score for score, url in url_scores[:3]]}")
            
            if relevant_urls:
                urls.extend(relevant_urls)
                seen_urls.update(relevant_urls)
                print(f"Strategy 2 (category scraping) found {len(relevant_urls)} relevant articles")
            
            print(f"Total articles after Strategy 2: {len(urls)}")
            print(f"Proceeding to Strategy 3 (Google search)...")
            
            # Strategy 2b: Enhanced title and content analysis for compound terms
            print("No URL matches found, doing enhanced content analysis...")
            
            title_matches = []
            # Check more articles for compound terms (increased for better coverage)
            articles_to_check = min(80, len(all_story_urls))
            
            for story_url in all_story_urls[:articles_to_check]:
                try:
                    # Use fresh random user agent for each article
                    article_headers = {
                        'User-Agent': self.get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive'
                    }
                    resp = requests.get(story_url, headers=article_headers, timeout=8)  # Reduced timeout for speed
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
                        
                        # Also check first paragraph for additional context
                        first_para = ""
                        para_elem = soup.find('p')
                        if para_elem:
                            first_para = para_elem.get_text()[:200].lower()  # First 200 chars
                        
                        combined_text = f"{title_text} {meta_desc} {first_para}"
                        
                        # Scoring for content matches
                        content_score = 0
                        
                        # Check for exact phrase match
                        if query.lower() in combined_text:
                            content_score += 20
                        
                        # Check for phrase variations (compound terms handling)
                        phrase_variations = [
                            query.lower().replace(' ', '-'),
                            query.lower().replace(' ', '_'),
                            query.lower()
                        ]
                        
                        # Special Shellharbour variations
                        if 'shellharbour' in query.lower():
                            phrase_variations.extend([
                                'shellharbour city council',
                                'shellharbour-city-council', 
                                'shell harbour council',
                                'shell-harbour-council'
                            ])
                        
                        for variation in phrase_variations:
                            if variation in combined_text:
                                content_score += 18  # Increased from 15
                                break
                        
                        # Check individual words
                        words_found = 0
                        for word in query_words:
                            if word in combined_text:
                                content_score += 5
                                words_found += 1
                                # Extra points if word is in title
                                if word in title_text:
                                    content_score += 3
                        
                        # Special handling for Shellharbour + Council combinations
                        if 'shellharbour' in query.lower():
                            shellharbour_variants = ['shellharbour', 'shell harbour', 'shell-harbour']
                            council_variants = ['council', 'city council', 'city-council']
                            
                            has_location = any(variant in combined_text for variant in shellharbour_variants)
                            has_council = any(variant in combined_text for variant in council_variants)
                            
                            if has_location and has_council:
                                content_score += 15  # Bonus for both location and council
                            elif has_location:
                                content_score += 8   # Some points for just location
                        
                        # Bonus for multiple words found
                        if len(query_words) > 1 and words_found > 1:
                            content_score += words_found * 3  # Increased multiplier
                        
                        # Bonus if words appear in title (more relevant than description)
                        title_words = sum(1 for word in query_words if word in title_text)
                        if title_words > 0:
                            content_score += title_words * 3
                        
                        if content_score > 0:
                            title_matches.append((content_score, story_url))
                            if len(title_matches) >= max_results:
                                break
                
                except Exception:
                    continue
                
                # Small delay to be respectful
                time.sleep(0.3)
            
            # Sort title matches by relevance
            title_matches.sort(reverse=True, key=lambda x: x[0])
            title_urls = [url for score, url in title_matches]
            
            print(f"Found {len(title_urls)} content matches")
            if title_matches:
                print(f"Top content scores: {[score for score, url in title_matches[:3]]}")
            
            if title_urls:
                urls.extend(title_urls)
                seen_urls.update(title_urls)
                print(f"Strategy 2 content analysis found {len(title_urls)} additional articles")
            
            print(f"Total articles after Strategy 2 content analysis: {len(urls)}")
            print(f"Proceeding to Strategy 3 (Google search)...")
            
            # Strategy 2c: If still no results for compound terms, try broader single-word search
            if len(query_words) > 1 and len(urls) < 3:
                print(f"Limited results for compound term, trying broader search...")
                broader_matches = []
                
                # Try searching with the first word only (often the location)
                primary_word = query_words[0]  # e.g., "shellharbour"
                
                for story_url in all_story_urls[:60]:  # Check more articles
                    try:
                        broader_headers = {
                            'User-Agent': self.get_random_user_agent(),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Connection': 'keep-alive'
                        }
                        resp = requests.get(story_url, headers=broader_headers, timeout=5)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.content, 'lxml')
                            
                            title_text = ""
                            title_elem = soup.find('h1')
                            if title_elem:
                                title_text = title_elem.get_text().lower()
                            
                            # Look for primary word in title or URL
                            url_lower = story_url.lower()
                            broad_score = 0
                            
                            if primary_word in title_text:
                                broad_score += 15
                            if primary_word in url_lower:
                                broad_score += 10
                            
                            # Check if any of the other query words appear nearby
                            for other_word in query_words[1:]:
                                if other_word in title_text or other_word in url_lower:
                                    broad_score += 5
                            
                            if broad_score > 0:
                                broader_matches.append((broad_score, story_url))
                                if len(broader_matches) >= 10:  # Get some additional results
                                    break
                    
                    except Exception:
                        continue
                    
                    time.sleep(0.2)
                
                # Add the best broader matches
                broader_matches.sort(reverse=True, key=lambda x: x[0])
                broader_urls = [url for score, url in broader_matches[:5]]  # Take top 5
                
                if broader_urls:
                    urls.extend(broader_urls)
                    seen_urls.update(broader_urls)
                    print(f"Strategy 2c (broader search) found {len(broader_urls)} additional articles")
            
            print(f"Enhanced category scraping completed: {len(urls)} articles found")
            return urls[:max_results]
        
        except Exception as e:
            print(f"Enhanced category scraping failed: {e}")
            return []
    def search_abc_news(self, query, max_results):
        """Searches ABC News for a given query."""
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
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
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
                print(f"Critical error - unable to send any response: {message}")

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print("Server starting on http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()
