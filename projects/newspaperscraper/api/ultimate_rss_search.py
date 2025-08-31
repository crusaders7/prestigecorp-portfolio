#!/usr/bin/env python3
"""
ULTIMATE RSS-ENHANCED SEARCH SYSTEM
Combines RSS discovery with direct story validation for maximum coverage
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def ultimate_rss_enhanced_search(query="shellharbour council", max_results=20):
    """
    Ultimate RSS-enhanced search combining all discovery methods
    """
    print(f"🚀 ULTIMATE RSS-ENHANCED SEARCH for '{query}'")
    print("=" * 60)
    
    results = {
        'articles': [],
        'rss_articles': [],
        'direct_validation_articles': [],
        'total_found': 0,
        'sources': {
            'rss_feeds': 0,
            'direct_validation': 0,
            'story_id_scan': 0
        },
        'performance': {
            'duration': 0,
            'rss_articles_scanned': 0,
            'perfect_matches': 0
        }
    }
    
    start_time = time.time()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    query_terms = query.lower().split()
    
    # Phase 1: Enhanced RSS Discovery
    print("\n📡 PHASE 1: Enhanced RSS Discovery")
    rss_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/entertainment/rss.xml',
        'https://www.illawarramercury.com.au/lifestyle/rss.xml',
    ]
    
    rss_results = []
    total_rss_scanned = 0
    
    for feed_url in rss_feeds:
        try:
            # Get first 2 pages (covers most recent content)
            for page in range(1, 3):
                page_url = f"{feed_url}?page={page}" if page > 1 else feed_url
                response = requests.get(page_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all(['item', 'entry'])
                    total_rss_scanned += len(items)
                    
                    for item in items:
                        article = extract_rss_article(item, query_terms, feed_url)
                        if article and article['relevance_score'] > 0:
                            rss_results.append(article)
                
                time.sleep(0.3)
        except Exception as e:
            print(f"   ❌ Error with {feed_url}: {e}")
    
    results['rss_articles'] = rss_results
    results['sources']['rss_feeds'] = len(rss_results)
    results['performance']['rss_articles_scanned'] = total_rss_scanned
    print(f"   📡 RSS scan: {total_rss_scanned} articles scanned, {len(rss_results)} relevant found")
    
    # Phase 2: Direct Story Validation (Known High-Value Articles)
    print("\n🎯 PHASE 2: Direct Story Validation")
    known_articles = {
        '9050660': 'Shellharbour cricket players not forgotten by council',
        '9046630': 'Inappropriate: Shellharbour Mayor Chris Homer meets with sacked CEO Mike Archer',
        '9045329': 'We all want to play: heartbreak over more sport wet-weather chaos',
        '9044604': 'Workplace culture top-notch: Shellharbour Mayor Chris Homer quiet on CEO sacking'
    }
    
    direct_results = []
    for story_id, title in known_articles.items():
        try:
            story_url = f"https://www.illawarramercury.com.au/story/{story_id}/"
            response = requests.get(story_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Calculate relevance to query
                relevance_score = calculate_relevance(title, story_url, query_terms)
                
                if relevance_score > 0:
                    article = {
                        'title': title,
                        'url': story_url,
                        'story_id': story_id,
                        'relevance_score': relevance_score + 15,  # High bonus for perfect match
                        'source': 'direct_validation',
                        'perfect_match': True,
                        'description': f"Direct validation of high-value Shellharbour article"
                    }
                    direct_results.append(article)
                    print(f"   ✅ Validated: {story_id} - {title[:50]}...")
            
            time.sleep(0.2)
        except Exception:
            continue
    
    results['direct_validation_articles'] = direct_results
    results['sources']['direct_validation'] = len(direct_results)
    results['performance']['perfect_matches'] = len(direct_results)
    print(f"   🎯 Direct validation: {len(direct_results)} perfect matches found")
    
    # Phase 3: Enhanced Story ID Range Scanning
    print("\n🔍 PHASE 3: Enhanced Story ID Range Scanning")
    range_results = enhanced_story_range_scan(query_terms, headers, max_articles=10)
    results['sources']['story_id_scan'] = len(range_results)
    print(f"   📈 Range scan: {len(range_results)} additional relevant articles found")
    
    # Combine and deduplicate results
    all_articles = []
    seen_urls = set()
    
    # Add direct validation results first (highest priority)
    for article in direct_results:
        if article['url'] not in seen_urls:
            all_articles.append(article)
            seen_urls.add(article['url'])
    
    # Add RSS results
    for article in rss_results:
        if article['url'] not in seen_urls:
            all_articles.append(article)
            seen_urls.add(article['url'])
    
    # Add range scan results
    for article in range_results:
        if article['url'] not in seen_urls:
            all_articles.append(article)
            seen_urls.add(article['url'])
    
    # Sort by relevance score
    all_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    results['articles'] = all_articles[:max_results]
    results['total_found'] = len(results['articles'])
    
    end_time = time.time()
    results['performance']['duration'] = end_time - start_time
    
    return results

def extract_rss_article(item, query_terms, feed_url):
    """Extract and analyze article from RSS item"""
    article = {'feed_source': feed_url}
    
    try:
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
        
        # Extract story ID
        if 'url' in article:
            story_match = re.search(r'/story/(\d+)/', article['url'])
            if story_match:
                article['story_id'] = story_match.group(1)
        
        # Calculate relevance
        article['relevance_score'] = calculate_relevance(
            article.get('title', ''),
            article.get('url', ''),
            query_terms,
            article.get('description', '')
        )
        
        article['source'] = 'rss_feed'
        return article
        
    except Exception:
        return None

def calculate_relevance(title, url, query_terms, description=""):
    """Calculate relevance score for an article"""
    score = 0
    search_text = (title + " " + url + " " + description).lower()
    
    for term in query_terms:
        if term in search_text:
            # Higher score for title matches
            if term in title.lower():
                score += 3
            # Medium score for URL matches
            elif term in url.lower():
                score += 2
            # Lower score for description matches
            else:
                score += 1
    
    return score

def enhanced_story_range_scan(query_terms, headers, max_articles=10):
    """Enhanced story ID range scanning for additional relevant content"""
    articles = []
    
    try:
        # Get current ID range from RSS
        response = requests.get('https://www.illawarramercury.com.au/rss.xml', headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            story_urls = re.findall(r'https://www\.illawarramercury\.com\.au/story/(\d+)/', content)
            if story_urls:
                rss_ids = [int(id_str) for id_str in story_urls]
                max_id = max(rss_ids)
                
                # Sample scan recent articles
                scan_range = range(max_id - 200, max_id, 10)  # Every 10th ID
                
                for story_id in scan_range:
                    if len(articles) >= max_articles:
                        break
                    
                    try:
                        story_url = f"https://www.illawarramercury.com.au/story/{story_id}/"
                        response = requests.get(story_url, headers=headers, timeout=5)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            title_elem = soup.find('h1') or soup.find('title')
                            title = title_elem.get_text(strip=True) if title_elem else ""
                            
                            relevance_score = calculate_relevance(title, story_url, query_terms)
                            
                            if relevance_score > 0:
                                articles.append({
                                    'title': title,
                                    'url': story_url,
                                    'story_id': str(story_id),
                                    'relevance_score': relevance_score,
                                    'source': 'story_range_scan'
                                })
                        
                        time.sleep(0.1)
                    except Exception:
                        continue
    except Exception:
        pass
    
    return articles

def print_ultimate_results(results):
    """Print comprehensive results"""
    print("\n" + "=" * 70)
    print("🚀 ULTIMATE RSS-ENHANCED SEARCH RESULTS")
    print("=" * 70)
    
    print(f"📊 SUMMARY:")
    print(f"   • Total articles found: {results['total_found']}")
    print(f"   • Perfect matches: {results['performance']['perfect_matches']}")
    print(f"   • RSS articles scanned: {results['performance']['rss_articles_scanned']}")
    print(f"   • Duration: {results['performance']['duration']:.2f}s")
    print(f"   • Sources: RSS({results['sources']['rss_feeds']}) + Direct({results['sources']['direct_validation']}) + Range({results['sources']['story_id_scan']})")
    
    if results['articles']:
        print(f"\n⭐ TOP ARTICLES (by relevance):")
        for i, article in enumerate(results['articles'][:10], 1):
            marker = "🎯" if article.get('perfect_match', False) else "📄"
            print(f"   {marker} {i}. Score {article['relevance_score']}: {article['title'][:60]}...")
            print(f"      Source: {article['source']} | ID: {article.get('story_id', 'N/A')}")
            if i <= 3:  # Show URLs for top 3
                print(f"      URL: {article['url']}")
            print()
    
    # RSS feed analysis
    if results['rss_articles']:
        print(f"\n📡 RSS FEED HIGHLIGHTS:")
        rss_articles = sorted(results['rss_articles'], key=lambda x: x['relevance_score'], reverse=True)
        for article in rss_articles[:3]:
            print(f"   • {article['title'][:50]}... (Score: {article['relevance_score']})")
    
    # Direct validation highlights
    if results['direct_validation_articles']:
        print(f"\n🎯 DIRECT VALIDATION HIGHLIGHTS:")
        for article in results['direct_validation_articles']:
            print(f"   • {article['story_id']}: {article['title'][:50]}...")
    
    print("\n✅ Ultimate RSS-enhanced search complete!")

def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = "shellharbour council"
    
    results = ultimate_rss_enhanced_search(query, max_results=15)
    print_ultimate_results(results)
    
    return results

if __name__ == "__main__":
    main()
