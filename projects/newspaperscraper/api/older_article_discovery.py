#!/usr/bin/env python3
"""
OLDER ARTICLE DISCOVERY SYSTEM
Advanced system for finding articles from weeks/months ago
Based on reverse engineering analysis of Illawarra Mercury
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime, timedelta
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

class OlderArticleDiscovery:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = 'https://www.illawarramercury.com.au'
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # From reverse engineering analysis
        self.current_id_range = {'min': 9003555, 'max': 9053686}
        self.daily_rate = 1671.0  # Estimated articles per day
        
        # Create local database for caching
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for caching discovered articles"""
        self.conn = sqlite3.connect('older_articles_cache.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                story_id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT,
                content TEXT,
                publish_date TEXT,
                discovered_date TEXT,
                relevance_score REAL,
                method TEXT
            )
        ''')
        self.conn.commit()
    
    def calculate_historical_id_ranges(self, days_back=30):
        """Calculate ID ranges for historical periods"""
        current_max = self.current_id_range['max']
        daily_rate = self.daily_rate
        
        ranges = {}
        for period in [7, 14, 30, 60, 90, 180, 365]:
            if period <= days_back:
                estimated_id = current_max - int(daily_rate * period)
                ranges[f'{period}_days_ago'] = {
                    'estimated_start': max(estimated_id - 1000, 1000000),  # Buffer
                    'estimated_end': estimated_id + 1000,
                    'period_days': period
                }
        
        return ranges
    
    def systematic_id_backtrack(self, query, days_back=30, max_articles=50):
        """
        Strategy 1: Systematic ID Backtracking
        Use calculated ID ranges to find older articles
        """
        print(f"🔍 SYSTEMATIC ID BACKTRACKING - {days_back} days")
        print("=" * 50)
        
        results = []
        ranges = self.calculate_historical_id_ranges(days_back)
        query_terms = query.lower().split()
        
        for period, range_info in ranges.items():
            print(f"\n📅 Scanning {period} (ID range: {range_info['estimated_start']} - {range_info['estimated_end']})")
            
            # Sample IDs from the range (every 50th to avoid overwhelming)
            start_id = range_info['estimated_start']
            end_id = range_info['estimated_end']
            sample_step = max(50, (end_id - start_id) // 100)  # Sample 100 IDs max
            
            sample_ids = list(range(start_id, end_id, sample_step))
            
            # Use threading for concurrent requests
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_id = {
                    executor.submit(self.check_article_by_id, story_id, query_terms): story_id 
                    for story_id in sample_ids[:20]  # Limit to 20 per period
                }
                
                for future in as_completed(future_to_id):
                    article = future.result()
                    if article and article['relevance_score'] > 0:
                        article['discovery_method'] = f'backtrack_{period}'
                        results.append(article)
                        print(f"   ✅ Found: {article['title'][:50]}... (ID: {article['story_id']})")
                        
                        if len(results) >= max_articles:
                            break
                
                if len(results) >= max_articles:
                    break
                    
                time.sleep(1)  # Rate limiting between periods
        
        print(f"\n📊 Backtracking found {len(results)} relevant articles")
        return results
    
    def check_article_by_id(self, story_id, query_terms):
        """Check if a specific article ID exists and is relevant"""
        try:
            url = f"{self.base_url}/story/{story_id}/"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title_elem = soup.find('h1') or soup.find('title')
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # Extract content for relevance check
                content_elems = soup.find_all(['p', 'div'], class_=re.compile(r'content|article|story'))
                content = ' '.join([elem.get_text(strip=True) for elem in content_elems[:5]])
                
                # Extract publish date
                date_elem = soup.find('time') or soup.find(attrs={'datetime': True})
                publish_date = ""
                if date_elem:
                    publish_date = date_elem.get('datetime', '') or date_elem.get_text(strip=True)
                
                # Calculate relevance
                relevance_score = self.calculate_relevance(title, content, query_terms)
                
                if relevance_score > 0:
                    article = {
                        'story_id': story_id,
                        'title': title,
                        'url': url,
                        'content': content[:500],  # First 500 chars
                        'publish_date': publish_date,
                        'relevance_score': relevance_score,
                        'discovered_date': datetime.now().isoformat()
                    }
                    
                    # Cache in database
                    self.cache_article(article)
                    return article
                    
        except Exception:
            pass
        
        return None
    
    def search_engine_discovery(self, query, days_back=30):
        """
        Strategy 4: Search Engine Cache Discovery
        Use Google site search with date filters
        """
        print(f"\n🌐 SEARCH ENGINE DISCOVERY - {days_back} days")
        print("=" * 50)
        
        results = []
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Google site search with date filter
        search_queries = [
            f'site:illawarramercury.com.au "{query}" after:{start_date.strftime("%Y-%m-%d")} before:{end_date.strftime("%Y-%m-%d")}',
            f'site:illawarramercury.com.au {query} filetype:html after:{start_date.strftime("%Y-%m-%d")}'
        ]
        
        print("   🔍 Using search engine discovery (simulated)")
        print("   💡 Actual implementation would use Google Custom Search API")
        print("   📝 Example queries:")
        for i, query_str in enumerate(search_queries, 1):
            print(f"      {i}. {query_str}")
        
        # Simulated results based on our known patterns
        simulated_results = [
            {'title': 'Historical Shellharbour Council Meeting Minutes', 'estimated_date': '2024-07-15'},
            {'title': 'Shellharbour Development Approvals Process', 'estimated_date': '2024-07-08'},
            {'title': 'Council Budget Discussions for Shellharbour', 'estimated_date': '2024-06-25'}
        ]
        
        print(f"   📊 Search engine would find ~{len(simulated_results)} additional articles")
        return simulated_results
    
    def internet_archive_discovery(self, query, days_back=90):
        """
        Strategy 5: Internet Archive Integration
        Use Wayback Machine to find historical snapshots
        """
        print(f"\n🏛️ INTERNET ARCHIVE DISCOVERY - {days_back} days")
        print("=" * 50)
        
        # Calculate target dates for snapshots
        target_dates = []
        today = datetime.now()
        for weeks_back in range(1, days_back // 7 + 1):
            snapshot_date = today - timedelta(weeks=weeks_back)
            target_dates.append(snapshot_date)
        
        print(f"   📅 Targeting {len(target_dates)} historical snapshots")
        
        # Wayback Machine API endpoints
        wayback_api = "http://archive.org/wayback/available"
        cdx_api = "http://web.archive.org/cdx/search/cdx"
        
        results = []
        
        for target_date in target_dates[:5]:  # Limit to 5 snapshots
            timestamp = target_date.strftime("%Y%m%d")
            target_url = f"{self.base_url}/news/"
            
            try:
                # Check if snapshot exists
                params = {
                    'url': target_url,
                    'timestamp': timestamp
                }
                
                print(f"   🔍 Checking snapshot for {target_date.strftime('%Y-%m-%d')}")
                print(f"      📞 Would query: {wayback_api}?url={target_url}&timestamp={timestamp}")
                
                # Simulated archive discovery
                simulated_archive_result = {
                    'date': target_date.strftime('%Y-%m-%d'),
                    'snapshot_url': f"http://web.archive.org/web/{timestamp}/{target_url}",
                    'status': 'available',
                    'estimated_articles': 15
                }
                results.append(simulated_archive_result)
                
            except Exception as e:
                print(f"   ❌ Error checking archive for {timestamp}: {e}")
        
        print(f"   📊 Archive discovery would find ~{sum(r.get('estimated_articles', 0) for r in results)} historical articles")
        return results
    
    def rss_deep_pagination(self, query, max_pages=50):
        """
        Strategy 3: RSS Historical Deep Pagination
        Attempt deep pagination through RSS feeds
        """
        print(f"\n📡 RSS DEEP PAGINATION - up to {max_pages} pages")
        print("=" * 50)
        
        rss_feeds = [
            'https://www.illawarramercury.com.au/rss.xml',
            'https://www.illawarramercury.com.au/news/rss.xml'
        ]
        
        results = []
        query_terms = query.lower().split()
        
        for feed_url in rss_feeds:
            print(f"\n   📡 Deep scanning: {feed_url}")
            
            # Test pagination in larger steps
            test_pages = [1, 5, 10, 20, 30, 40, 50, 100, 200]
            working_pages = []
            
            for page in test_pages:
                try:
                    page_url = f"{feed_url}?page={page}"
                    response = self.session.get(page_url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'xml')
                        items = soup.find_all(['item', 'entry'])
                        
                        if items:
                            working_pages.append(page)
                            
                            # Check for older content
                            for item in items[:5]:  # Check first 5 items
                                article = self.extract_rss_article(item, query_terms)
                                if article and article['relevance_score'] > 0:
                                    article['discovery_method'] = f'rss_deep_page_{page}'
                                    results.append(article)
                            
                            print(f"      ✅ Page {page}: {len(items)} articles")
                        else:
                            print(f"      ❌ Page {page}: No articles")
                            break
                    else:
                        print(f"      ❌ Page {page}: Status {response.status_code}")
                        
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"      ❌ Page {page}: Error {e}")
                    continue
            
            print(f"   📊 RSS feed supports pages: {working_pages}")
        
        print(f"   📊 RSS deep pagination found {len(results)} relevant articles")
        return results
    
    def extract_rss_article(self, item, query_terms):
        """Extract article from RSS item"""
        try:
            title_elem = item.find('title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            link_elem = item.find('link')
            url = link_elem.get_text(strip=True) if link_elem else ""
            
            desc_elem = item.find(['description', 'summary'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract story ID
            story_id = ""
            story_match = re.search(r'/story/(\d+)/', url)
            if story_match:
                story_id = story_match.group(1)
            
            relevance_score = self.calculate_relevance(title, description, query_terms)
            
            if relevance_score > 0:
                return {
                    'story_id': story_id,
                    'title': title,
                    'url': url,
                    'content': description,
                    'relevance_score': relevance_score,
                    'discovered_date': datetime.now().isoformat()
                }
        except Exception:
            pass
        
        return None
    
    def calculate_relevance(self, title, content, query_terms):
        """Calculate relevance score"""
        score = 0
        search_text = (title + " " + content).lower()
        
        for term in query_terms:
            if term in search_text:
                if term in title.lower():
                    score += 3
                else:
                    score += 1
        
        return score
    
    def cache_article(self, article):
        """Cache article in local database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (story_id, title, url, content, publish_date, discovered_date, relevance_score, method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['story_id'],
                article['title'],
                article['url'],
                article['content'],
                article.get('publish_date', ''),
                article['discovered_date'],
                article['relevance_score'],
                article.get('discovery_method', 'unknown')
            ))
            self.conn.commit()
        except Exception:
            pass
    
    def comprehensive_older_article_search(self, query, days_back=30, max_results=20):
        """
        Comprehensive search combining all strategies
        """
        print(f"🚀 COMPREHENSIVE OLDER ARTICLE SEARCH")
        print(f"Query: '{query}' | Looking back: {days_back} days")
        print("=" * 70)
        
        all_results = []
        
        # Strategy 1: Systematic ID Backtracking
        backtrack_results = self.systematic_id_backtrack(query, days_back, max_results // 2)
        all_results.extend(backtrack_results)
        
        # Strategy 3: RSS Deep Pagination
        rss_results = self.rss_deep_pagination(query, max_pages=20)
        all_results.extend(rss_results)
        
        # Strategy 4: Search Engine Discovery (simulated)
        search_results = self.search_engine_discovery(query, days_back)
        
        # Strategy 5: Internet Archive (simulated)
        archive_results = self.internet_archive_discovery(query, days_back)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for article in all_results:
            if article['url'] not in seen_urls:
                unique_results.append(article)
                seen_urls.add(article['url'])
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return unique_results[:max_results]
    
    def print_results(self, results, search_results=None, archive_results=None):
        """Print comprehensive results"""
        print("\n" + "=" * 70)
        print("📊 OLDER ARTICLE DISCOVERY RESULTS")
        print("=" * 70)
        
        print(f"🎯 Found {len(results)} older articles")
        
        if results:
            print("\n⭐ DISCOVERED ARTICLES:")
            for i, article in enumerate(results, 1):
                method = article.get('discovery_method', 'unknown')
                print(f"\n   {i}. {article['title'][:60]}...")
                print(f"      📊 Relevance: {article['relevance_score']}")
                print(f"      🔍 Method: {method}")
                print(f"      🔗 ID: {article['story_id']}")
                print(f"      📅 Date: {article.get('publish_date', 'Unknown')}")
                if i <= 3:  # Show URLs for top 3
                    print(f"      🌐 URL: {article['url']}")
        
        if search_results:
            print(f"\n🌐 SEARCH ENGINE POTENTIAL: {len(search_results)} additional articles")
        
        if archive_results:
            print(f"\n🏛️ ARCHIVE POTENTIAL: {sum(r.get('estimated_articles', 0) for r in archive_results)} historical articles")
        
        print("\n✅ Older article discovery complete!")
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main execution"""
    import sys
    
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else "shellharbour council"
    days_back = 60  # Look back 2 months
    
    discovery = OlderArticleDiscovery()
    
    try:
        results = discovery.comprehensive_older_article_search(query, days_back, max_results=15)
        discovery.print_results(results)
        
        # Show database stats
        cursor = discovery.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        cached_count = cursor.fetchone()[0]
        print(f"\n💾 Cached articles in database: {cached_count}")
        
    finally:
        discovery.close()

if __name__ == "__main__":
    main()
