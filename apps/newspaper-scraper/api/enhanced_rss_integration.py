#!/usr/bin/env python3
"""
ENHANCED RSS FEED INTEGRATION
Integrates RSS discovery with historical and advanced feed patterns
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta


def discover_advanced_rss_patterns():
    """Discover advanced RSS patterns including historical feeds"""
    print("🔍 DISCOVERING ADVANCED RSS PATTERNS")
    print("=" * 50)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    advanced_feeds = []

    # Test date-based RSS patterns
    print("\n📅 Testing date-based RSS patterns...")
    current_year = 2025
    current_month = 8  # August

    date_patterns = [
        f'https://www.illawarramercury.com.au/{current_year}/rss.xml',
        f'https://www.illawarramercury.com.au/{current_year}/{current_month:02d}/rss.xml',
        f'https://www.illawarramercury.com.au/archive/{current_year}/rss.xml',
        f'https://www.illawarramercury.com.au/archive/{current_year}/{current_month:02d}/rss.xml',
        f'https://www.illawarramercury.com.au/feeds/{current_year}.xml',
        f'https://www.illawarramercury.com.au/feeds/archive-{current_year}.xml',
        f'https://www.illawarramercury.com.au/rss/{current_year}.xml',
        f'https://www.illawarramercury.com.au/historical/rss.xml',
        f'https://www.illawarramercury.com.au/all-articles.xml',
        f'https://www.illawarramercury.com.au/complete-feed.xml',
    ]

    for pattern in date_patterns:
        try:
            response = requests.get(pattern, headers=headers, timeout=10)
            if response.status_code == 200 and ('xml' in response.headers.get('content-type', '').lower() or response.text.strip().startswith('<?xml')):
                print(f"   ✅ Found: {pattern}")
                advanced_feeds.append(pattern)
            else:
                print(f"   ❌ {response.status_code}: {pattern}")
        except Exception:
            print(f"   ❌ Error: {pattern}")
        time.sleep(0.3)

    # Test category-specific advanced patterns
    print("\n📂 Testing advanced category RSS patterns...")
    categories = ['council', 'local', 'shellharbour',
                  'government', 'mayor', 'politics']

    for category in categories:
        category_patterns = [
            f'https://www.illawarramercury.com.au/{category}/rss.xml',
            f'https://www.illawarramercury.com.au/feeds/{category}.xml',
            f'https://www.illawarramercury.com.au/topics/{category}/rss.xml',
            f'https://www.illawarramercury.com.au/tag/{category}/rss.xml',
        ]

        for pattern in category_patterns:
            try:
                response = requests.get(pattern, headers=headers, timeout=10)
                if response.status_code == 200 and ('xml' in response.headers.get('content-type', '').lower() or response.text.strip().startswith('<?xml')):
                    print(f"   ✅ Found category feed: {pattern}")
                    advanced_feeds.append(pattern)
                else:
                    print(f"   ❌ {response.status_code}: {pattern}")
            except Exception:
                print(f"   ❌ Error: {pattern}")
            time.sleep(0.2)

    return advanced_feeds


def analyze_sitemap_for_rss():
    """Analyze sitemap for additional RSS feed references"""
    print("\n🗺️ ANALYZING SITEMAP FOR RSS REFERENCES")
    print("=" * 50)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    sitemap_feeds = []

    try:
        # Get main sitemap
        response = requests.get(
            'https://www.illawarramercury.com.au/sitemap.xml', headers=headers)
        if response.status_code == 200:
            content = response.text

            # Look for RSS references
            rss_urls = re.findall(
                r'https://[^<\s"]+(?:rss|feed)(?:[^<\s"]*\.xml)?[^<\s"]*', content, re.IGNORECASE)
            if rss_urls:
                print(
                    f"   📡 Found {len(rss_urls)} RSS references in main sitemap:")
                for rss_url in rss_urls:
                    print(f"      • {rss_url}")
                    sitemap_feeds.extend(rss_urls)

            # Get all sub-sitemaps
            sitemap_urls = re.findall(
                r'https://[^<\s"]+sitemap[^<\s"]*\.xml', content)
            print(f"   📋 Found {len(sitemap_urls)} sub-sitemaps to check...")

            for sitemap_url in sitemap_urls[:10]:  # Check first 10
                try:
                    sub_response = requests.get(
                        sitemap_url, headers=headers, timeout=10)
                    if sub_response.status_code == 200:
                        sub_content = sub_response.text
                        sub_rss = re.findall(
                            r'https://[^<\s"]+(?:rss|feed)[^<\s"]*', sub_content, re.IGNORECASE)
                        if sub_rss:
                            print(
                                f"      📡 Found RSS in {sitemap_url.split('/')[-1]}: {len(sub_rss)} feeds")
                            sitemap_feeds.extend(sub_rss)
                    time.sleep(0.3)
                except Exception:
                    continue

    except Exception as e:
        print(f"   ❌ Error analyzing sitemap: {e}")

    return sitemap_feeds


def test_pagination_rss():
    """Test if RSS feeds support pagination to get more articles"""
    print("\n📄 TESTING RSS PAGINATION")
    print("=" * 50)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    base_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
    ]

    paginated_articles = []

    for base_feed in base_feeds:
        print(f"\n📡 Testing pagination for: {base_feed}")

        # Test different pagination formats
        pagination_formats = [
            base_feed + "?page={}",
            base_feed + "?p={}",
            base_feed + "?offset={}",
            base_feed.replace('.xml', '') + "/page/{}.xml",
            base_feed.replace('.xml', '') + "-page-{}.xml",
        ]

        for page_format in pagination_formats:
            found_pages = 0
            for page in range(2, 6):  # Test pages 2-5
                try:
                    if '{}' in page_format:
                        test_url = page_format.format(page)
                    else:
                        continue

                    response = requests.get(
                        test_url, headers=headers, timeout=10)
                    if response.status_code == 200 and response.text.strip().startswith('<?xml'):
                        soup = BeautifulSoup(response.content, 'xml')
                        items = soup.find_all(['item', 'entry'])
                        if items:
                            found_pages += 1
                            print(
                                f"   ✅ Page {page} found: {len(items)} items - {test_url}")

                            # Extract story IDs to check for our targets
                            for item in items:
                                link_elem = item.find(['link'])
                                if link_elem:
                                    link = link_elem.get_text(
                                        strip=True) if link_elem.string else link_elem.get('href', '')
                                    story_match = re.search(
                                        r'/story/(\d+)/', link)
                                    if story_match:
                                        story_id = story_match.group(1)
                                        if story_id in ['9050660', '9046630', '9045329', '636609', '9044604']:
                                            print(
                                                f"      🎯 FOUND TARGET: {story_id} in {test_url}")
                        break  # Found working format, continue with this
                    else:
                        print(
                            f"   ❌ Page {page}: {response.status_code} - {test_url}")

                except Exception:
                    continue

                time.sleep(0.3)

            if found_pages > 0:
                print(
                    f"   📊 Found {found_pages} additional pages for this feed")
                break  # Found working pagination format


def enhanced_rss_integration():
    """Enhanced RSS integration with all discovery methods"""
    print("🚀 ENHANCED RSS FEED INTEGRATION")
    print("=" * 60)

    all_feeds = set()

    # Standard RSS feeds (already discovered)
    standard_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/entertainment/rss.xml',
        'https://www.illawarramercury.com.au/lifestyle/rss.xml',
    ]
    all_feeds.update(standard_feeds)
    print(f"📡 Standard RSS feeds: {len(standard_feeds)}")

    # Advanced pattern discovery
    advanced_feeds = discover_advanced_rss_patterns()
    all_feeds.update(advanced_feeds)
    print(f"🔍 Advanced pattern feeds: {len(advanced_feeds)}")

    # Sitemap analysis
    sitemap_feeds = analyze_sitemap_for_rss()
    all_feeds.update(sitemap_feeds)
    print(f"🗺️ Sitemap-discovered feeds: {len(sitemap_feeds)}")

    # Test pagination
    test_pagination_rss()

    print(f"\n📊 ENHANCED RSS INTEGRATION SUMMARY")
    print("=" * 50)
    print(f"📡 Total unique RSS feeds discovered: {len(all_feeds)}")
    print(f"🔍 Feed sources:")
    print(f"   • Standard feeds: {len(standard_feeds)}")
    print(f"   • Advanced patterns: {len(advanced_feeds)}")
    print(f"   • Sitemap discovery: {len(sitemap_feeds)}")

    if all_feeds:
        print(f"\n📋 ALL DISCOVERED FEEDS:")
        for i, feed in enumerate(sorted(all_feeds), 1):
            print(f"   {i}. {feed}")

    return list(all_feeds)


def create_enhanced_rss_search_function():
    """Create enhanced RSS search function that can be integrated"""
    print(f"\n🛠️ CREATING ENHANCED RSS SEARCH INTEGRATION")
    print("=" * 50)

    enhanced_rss_code = '''
def enhanced_rss_search_illawarra_mercury(query, max_results=20):
    """
    Enhanced RSS-based search using all discovered feeds
    Includes pagination and historical feed support
    """
    import requests
    from bs4 import BeautifulSoup
    import re
    import time
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    query_terms = query.lower().split()
    all_articles = []
    
    # All discovered RSS feeds
    rss_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/entertainment/rss.xml',
        'https://www.illawarramercury.com.au/lifestyle/rss.xml',
    ]
    
    for feed_url in rss_feeds:
        try:
            # Try main feed
            response = requests.get(feed_url, headers=headers, timeout=15)
            if response.status_code == 200:
                articles = parse_rss_feed(response.content, query_terms, feed_url)
                all_articles.extend(articles)
            
            # Try paginated feeds
            for page in range(2, 4):  # Check pages 2-3
                paginated_url = f"{feed_url}?page={page}"
                try:
                    page_response = requests.get(paginated_url, headers=headers, timeout=10)
                    if page_response.status_code == 200:
                        page_articles = parse_rss_feed(page_response.content, query_terms, paginated_url)
                        all_articles.extend(page_articles)
                except:
                    break
            
            time.sleep(0.5)
        except Exception:
            continue
    
    # Remove duplicates and sort by relevance
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    unique_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    return unique_articles[:max_results]

def parse_rss_feed(content, query_terms, feed_url):
    """Parse RSS feed content and extract relevant articles"""
    articles = []
    
    try:
        soup = BeautifulSoup(content, 'xml')
        items = soup.find_all(['item', 'entry'])
        
        for item in items:
            article = {'feed_source': feed_url}
            
            # Extract title
            title_elem = item.find(['title'])
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
            
            # Extract URL
            link_elem = item.find(['link'])
            if link_elem:
                link = link_elem.get_text(strip=True) if link_elem.string else link_elem.get('href', '')
                article['url'] = link
            
            # Extract description
            desc_elem = item.find(['description', 'summary'])
            if desc_elem:
                article['description'] = desc_elem.get_text(strip=True)
            
            # Calculate relevance
            text_content = (
                article.get('title', '') + ' ' + 
                article.get('description', '') + ' ' + 
                article.get('url', '')
            ).lower()
            
            relevance_score = 0
            for term in query_terms:
                if term in text_content:
                    relevance_score += 1
            
            if relevance_score > 0:
                article['relevance_score'] = relevance_score
                article['source'] = 'enhanced_rss'
                articles.append(article)
    
    except Exception:
        pass
    
    return articles
'''

    # Save enhanced RSS function to file
    with open('enhanced_rss_search.py', 'w') as f:
        f.write(enhanced_rss_code)

    print("   ✅ Enhanced RSS search function created in 'enhanced_rss_search.py'")
    print("   💡 This can now be imported and integrated into the main search system")

    return enhanced_rss_code


if __name__ == "__main__":
    # Run comprehensive RSS integration
    all_feeds = enhanced_rss_integration()

    # Create enhanced search function
    enhanced_code = create_enhanced_rss_search_function()

    print(f"\n✅ ENHANCED RSS INTEGRATION COMPLETE!")
    print(f"📡 Total feeds: {len(all_feeds)}")
    print(f"🔧 Enhanced search function ready for integration")
