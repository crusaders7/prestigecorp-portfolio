#!/usr/bin/env python3
"""
Strategy Performance Tester for Newspaper Scraper
Tests each search strategy individually to determine which works best for Shellharbour Council articles
"""

import sys
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, unquote
import re
import random

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'projects', 'newspaperscraper', 'api'))

class StrategyTester:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]
        
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def test_strategy_1_site_search(self, query, max_results=20):
        """Test Strategy 1: Site's own search function"""
        print(f"\n{'='*60}")
        print(f"TESTING STRATEGY 1: Site Search")
        print(f"{'='*60}")
        
        urls = []
        seen_urls = set()
        
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
            print(f"Testing URL: {search_url}")
            
            resp = requests.get(search_url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'lxml')
            
            # Try multiple selectors for search results
            selectors_tried = []
            for selector in [
                'article a[href*="/story/"]',
                '.search-result a[href*="/story/"]',
                '.story-block a[href*="/story/"]',
                'h3 a[href*="/story/"]',
                'h2 a[href*="/story/"]',
                'a[href*="/story/"]'
            ]:
                links = soup.select(selector)
                selectors_tried.append(f"{selector}: {len(links)} links")
                if links:
                    print(f"✓ Found {len(links)} links with selector: {selector}")
                    for link in links:
                        href = link.get('href', '')
                        if '/story/' in href:
                            full_url = urljoin("https://www.illawarramercury.com.au", href)
                            clean_url = full_url.split('#')[0].split('?')[0]
                            if clean_url not in seen_urls:
                                urls.append(clean_url)
                                seen_urls.add(clean_url)
                    break
            
            print(f"All selectors tried: {selectors_tried}")
            print(f"Strategy 1 Result: {len(urls)} unique URLs found")
            
            return urls, len(urls), "Success" if urls else "No results found"
            
        except Exception as e:
            print(f"Strategy 1 Failed: {e}")
            return [], 0, f"Error: {e}"
    
    def test_strategy_2_category_scraping(self, query, max_results=20):
        """Test Strategy 2: Category scraping with URL analysis"""
        print(f"\n{'='*60}")
        print(f"TESTING STRATEGY 2: Category Scraping")
        print(f"{'='*60}")
        
        urls = []
        seen_urls = set()
        
        try:
            # Scrape categories
            categories = [
                "https://www.illawarramercury.com.au/",
                "https://www.illawarramercury.com.au/news/",
                "https://www.illawarramercury.com.au/news/local-news/"
            ]
            
            all_story_urls = []
            for category_url in categories:
                try:
                    headers = {
                        'User-Agent': self.get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Connection': 'keep-alive'
                    }
                    
                    print(f"Scraping category: {category_url}")
                    resp = requests.get(category_url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.content, 'lxml')
                    
                    category_urls = 0
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href:
                            full_url = urljoin(category_url, href)
                            clean_url = full_url.split('#')[0].split('?')[0]
                            if clean_url not in all_story_urls:
                                all_story_urls.append(clean_url)
                                category_urls += 1
                    
                    print(f"  Found {category_urls} story URLs from this category")
                    
                except Exception as e:
                    print(f"  Failed to scrape {category_url}: {e}")
            
            print(f"Total story URLs found: {len(all_story_urls)}")
            
            # URL keyword analysis
            query_lower = query.lower()
            query_words = [word.lower() for word in query.split() if len(word) > 2]
            
            query_variations = [
                query_lower,
                query_lower.replace(' ', '-'),
                query_lower.replace(' ', '_'),
                query_lower.replace('council', 'city-council'),
                'shellharbour-city-council' if 'shellharbour' in query_lower else None,
                'shell-harbour' if 'shellharbour' in query_lower else None
            ]
            query_variations = [v for v in query_variations if v]
            
            print(f"Query variations: {query_variations}")
            print(f"Query words: {query_words}")
            
            # Score URLs
            url_scores = []
            for story_url in all_story_urls:
                url_text = story_url.lower()
                score = 0
                
                # Check for exact phrase matches
                for variation in query_variations:
                    if variation in url_text:
                        score += 30
                        break
                
                # Check individual words
                words_found = 0
                for word in query_words:
                    if word in url_text:
                        score += 10
                        words_found += 1
                        if '/story/' in url_text and word in url_text.split('/story/')[-1]:
                            score += 5
                
                # Special handling for shellharbour
                if 'shellharbour' in query_lower:
                    if 'shell-harbour' in url_text or 'shellharbour' in url_text:
                        score += 8
                
                if len(query_words) > 1 and words_found > 1:
                    score += words_found * 3
                
                if score > 0:
                    url_scores.append((score, story_url))
            
            # Sort by score
            url_scores.sort(reverse=True, key=lambda x: x[0])
            relevant_urls = [url for score, url in url_scores[:max_results]]
            
            print(f"URLs with relevance scores:")
            for i, (score, url) in enumerate(url_scores[:10], 1):
                print(f"  {i}. Score {score}: {url}")
            
            return relevant_urls, len(relevant_urls), f"Success - analyzed {len(all_story_urls)} URLs"
            
        except Exception as e:
            print(f"Strategy 2 Failed: {e}")
            return [], 0, f"Error: {e}"
    
    def test_strategy_3_google_search(self, query, max_results=20):
        """Test Strategy 3: Google site search"""
        print(f"\n{'='*60}")
        print(f"TESTING STRATEGY 3: Google Search")
        print(f"{'='*60}")
        
        urls = []
        seen_urls = set()
        
        try:
            search_queries = [
                f'site:illawarramercury.com.au "{query}"',
                f'site:illawarramercury.com.au {query}'
            ]
            
            for search_query in search_queries:
                print(f"Testing Google query: {search_query}")
                google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&num=20"
                
                headers = {
                    'User-Agent': self.get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }
                
                resp = requests.get(google_url, headers=headers, timeout=12)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'lxml')
                
                found_in_query = 0
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if '/url?q=' in href:
                        match = re.search(r'/url\?q=([^&]+)', href)
                        if match:
                            actual_url = unquote(match.group(1))
                            if 'illawarramercury.com.au/story/' in actual_url:
                                clean_url = actual_url.split('#')[0].split('?')[0]
                                if clean_url not in seen_urls:
                                    seen_urls.add(clean_url)
                                    urls.append(clean_url)
                                    found_in_query += 1
                
                print(f"  Found {found_in_query} new URLs with this query")
                time.sleep(2)  # Be respectful to Google
            
            return urls, len(urls), f"Success - tested {len(search_queries)} queries"
            
        except Exception as e:
            print(f"Strategy 3 Failed: {e}")
            return [], 0, f"Error: {e}"
    
    def test_strategy_4_duckduckgo(self, query, max_results=20):
        """Test Strategy 4: DuckDuckGo search"""
        print(f"\n{'='*60}")
        print(f"TESTING STRATEGY 4: DuckDuckGo Search")
        print(f"{'='*60}")
        
        urls = []
        seen_urls = set()
        
        try:
            ddg_search_url = "https://html.duckduckgo.com/html/"
            params = {'q': f'site:illawarramercury.com.au {query}'}
            
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            
            print(f"Testing DuckDuckGo with query: {params['q']}")
            
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
            
            return urls, len(urls), "Success" if urls else "No results found"
            
        except Exception as e:
            print(f"Strategy 4 Failed: {e}")
            return [], 0, f"Error: {e}"
    
    def run_comprehensive_test(self, query="shellharbour council"):
        """Run all strategies and compare results"""
        print(f"\n{'#'*80}")
        print(f"COMPREHENSIVE STRATEGY TESTING")
        print(f"Query: '{query}'")
        print(f"{'#'*80}")
        
        results = {}
        
        # Test each strategy
        strategies = [
            ("Strategy 1: Site Search", self.test_strategy_1_site_search),
            ("Strategy 2: Category Scraping", self.test_strategy_2_category_scraping),
            ("Strategy 3: Google Search", self.test_strategy_3_google_search),
            ("Strategy 4: DuckDuckGo Search", self.test_strategy_4_duckduckgo)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                start_time = time.time()
                urls, count, status = strategy_func(query)
                end_time = time.time()
                
                results[strategy_name] = {
                    'urls': urls,
                    'count': count,
                    'status': status,
                    'time': round(end_time - start_time, 2)
                }
                
                print(f"\n{strategy_name}: {count} URLs in {results[strategy_name]['time']}s")
                
            except Exception as e:
                results[strategy_name] = {
                    'urls': [],
                    'count': 0,
                    'status': f"Failed: {e}",
                    'time': 0
                }
        
        # Summary report
        print(f"\n{'='*80}")
        print(f"FINAL RESULTS SUMMARY")
        print(f"{'='*80}")
        
        # Sort by effectiveness
        sorted_results = sorted(results.items(), key=lambda x: x[1]['count'], reverse=True)
        
        print(f"{'Strategy':<30} {'URLs Found':<12} {'Time (s)':<10} {'Status'}")
        print(f"{'-'*30} {'-'*12} {'-'*10} {'-'*20}")
        
        for strategy_name, data in sorted_results:
            print(f"{strategy_name:<30} {data['count']:<12} {data['time']:<10} {data['status']}")
        
        # Show best performing strategy details
        if sorted_results:
            best_strategy, best_data = sorted_results[0]
            print(f"\n🏆 BEST PERFORMING STRATEGY: {best_strategy}")
            print(f"   Found {best_data['count']} URLs in {best_data['time']} seconds")
            
            if best_data['urls']:
                print(f"\n   Sample URLs found:")
                for i, url in enumerate(best_data['urls'][:5], 1):
                    print(f"   {i}. {url}")
        
        # Check for overlaps between strategies
        all_urls = set()
        for strategy_name, data in results.items():
            all_urls.update(data['urls'])
        
        print(f"\n📊 OVERLAP ANALYSIS:")
        print(f"   Total unique URLs across all strategies: {len(all_urls)}")
        
        for strategy_name, data in results.items():
            if data['urls']:
                unique_to_this = set(data['urls']) - set().union(*[other_data['urls'] for other_name, other_data in results.items() if other_name != strategy_name])
                print(f"   {strategy_name}: {len(unique_to_this)} URLs unique to this strategy")
        
        return results

def main():
    """Main test function"""
    tester = StrategyTester()
    
    # Test with the specific query we know has results
    results = tester.run_comprehensive_test("shellharbour council")
    
    # Recommendations
    print(f"\n{'='*80}")
    print(f"RECOMMENDATIONS")
    print(f"{'='*80}")
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]['count'], reverse=True)
    
    if sorted_results and sorted_results[0][1]['count'] > 0:
        best_strategy = sorted_results[0][0]
        print(f"✅ Implement {best_strategy} as the primary strategy")
        
        # Check if multiple strategies are valuable
        strategies_with_results = [name for name, data in sorted_results if data['count'] > 0]
        
        if len(strategies_with_results) > 1:
            print(f"✅ Consider combining multiple strategies:")
            for strategy in strategies_with_results[:3]:  # Top 3
                count = results[strategy]['count']
                time_taken = results[strategy]['time']
                print(f"   - {strategy}: {count} URLs ({time_taken}s)")
        
        # Performance optimization suggestions
        fastest_with_results = min(
            [(name, data) for name, data in sorted_results if data['count'] > 0],
            key=lambda x: x[1]['time']
        )
        
        if fastest_with_results:
            print(f"⚡ Fastest effective strategy: {fastest_with_results[0]} ({fastest_with_results[1]['time']}s)")
    
    else:
        print(f"❌ No strategies found results for 'shellharbour council'")
        print(f"💡 Consider:")
        print(f"   - Checking if recent articles exist in the feeds")
        print(f"   - Testing with different query variations")
        print(f"   - Investigating site's search functionality")

if __name__ == "__main__":
    main()
