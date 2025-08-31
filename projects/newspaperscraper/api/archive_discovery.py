#!/usr/bin/env python3
"""
Archive and Historical Content Discovery
Focuses on finding older articles through archive patterns and historical sitemaps
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta

def analyze_story_id_patterns():
    """Analyze the story ID patterns to understand dating"""
    print('\n🔍 ANALYZING STORY ID PATTERNS')
    print('=' * 50)
    
    target_ids = [9050660, 9046630, 9045329, 636609, 9044604]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Get recent articles from RSS to establish ID patterns
    print('📊 Getting recent article IDs from RSS...')
    try:
        response = requests.get('https://www.illawarramercury.com.au/rss.xml', headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            story_urls = re.findall(r'https://www\.illawarramercury\.com\.au/story/(\d+)/', content)
            recent_ids = [int(id_str) for id_str in story_urls]
            
            if recent_ids:
                print(f'   📈 Recent IDs range: {min(recent_ids)} - {max(recent_ids)}')
                print(f'   📊 Average recent ID: {sum(recent_ids)/len(recent_ids):.0f}')
                
                # Analyze our target IDs relative to recent ones
                print('\n🎯 Target ID Analysis:')
                for target_id in target_ids:
                    if target_id > max(recent_ids):
                        print(f'   • {target_id}: NEWER than RSS content!')
                    elif target_id > min(recent_ids):
                        print(f'   • {target_id}: In recent range but missing from RSS')
                    else:
                        print(f'   • {target_id}: OLDER than RSS content - likely archived')
                
                return min(recent_ids), max(recent_ids)
    except Exception as e:
        print(f'   ❌ Error analyzing RSS: {str(e)}')
    
    return None, None

def test_archive_patterns():
    """Test various archive URL patterns"""
    print('\n📚 TESTING ARCHIVE PATTERNS')
    print('=' * 50)
    
    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found_articles = []
    
    # Test year/month archive patterns
    current_year = datetime.now().year
    years_to_test = [current_year, current_year - 1, current_year - 2]
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    
    archive_patterns = [
        'https://www.illawarramercury.com.au/archive/{year}/',
        'https://www.illawarramercury.com.au/archive/{year}/{month}/',
        'https://www.illawarramercury.com.au/{year}/',
        'https://www.illawarramercury.com.au/{year}/{month}/',
        'https://www.illawarramercury.com.au/news/{year}/',
        'https://www.illawarramercury.com.au/news/{year}/{month}/',
    ]
    
    print('🗓️ Testing recent months...')
    for year in [current_year]:  # Focus on current year first
        for month in ['08', '09', '10', '11', '12']:  # Recent months
            for pattern in archive_patterns:
                archive_url = pattern.format(year=year, month=month)
                print(f'\n📅 Testing: {archive_url}')
                
                try:
                    response = requests.get(archive_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        article_links = []
                        
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if '/story/' in href and 'illawarramercury.com.au' in href:
                                article_links.append(href)
                        
                        if article_links:
                            print(f'   ✅ Found {len(article_links)} articles')
                            
                            # Check for targets
                            for link in article_links:
                                for target_id in target_ids:
                                    if target_id in link:
                                        print(f'   🎯 FOUND TARGET: {target_id} in {link}')
                                        found_articles.append((target_id, link))
                        else:
                            print(f'   📄 Archive exists but no articles found')
                    else:
                        print(f'   ❌ Status: {response.status_code}')
                except Exception as e:
                    print(f'   ❌ Error: {str(e)}')
                
                time.sleep(0.3)
    
    return found_articles

def check_comprehensive_sitemaps():
    """Check all available sitemaps more thoroughly"""
    print('\n🗺️ COMPREHENSIVE SITEMAP ANALYSIS')
    print('=' * 50)
    
    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found_articles = []
    
    # Get main sitemap to find all available sitemaps
    try:
        response = requests.get('https://www.illawarramercury.com.au/sitemap.xml', headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            sitemap_urls = re.findall(r'https://[^<\s"]+\.xml', content)
            
            print(f'📋 Found {len(sitemap_urls)} sitemaps to check')
            
            for i, sitemap_url in enumerate(sitemap_urls):
                print(f'\n📄 [{i+1}/{len(sitemap_urls)}] Checking: {sitemap_url}')
                
                try:
                    sitemap_response = requests.get(sitemap_url, headers=headers, timeout=10)
                    if sitemap_response.status_code == 200:
                        sitemap_content = sitemap_response.text
                        
                        # Look for story URLs
                        story_urls = re.findall(r'https://www\.illawarramercury\.com\.au/story/\d+/[^<\s"]+', sitemap_content)
                        
                        if story_urls:
                            print(f'   📰 Found {len(story_urls)} story URLs')
                            
                            # Extract and analyze story IDs
                            story_ids = []
                            for url in story_urls:
                                match = re.search(r'/story/(\d+)/', url)
                                if match:
                                    story_ids.append(int(match.group(1)))
                            
                            if story_ids:
                                print(f'   📊 ID range: {min(story_ids)} - {max(story_ids)}')
                            
                            # Check for targets
                            for url in story_urls:
                                for target_id in target_ids:
                                    if target_id in url:
                                        print(f'   🎯 FOUND TARGET: {target_id} in {url}')
                                        found_articles.append((target_id, url))
                        else:
                            print(f'   📄 No story URLs in this sitemap')
                    else:
                        print(f'   ❌ Status: {sitemap_response.status_code}')
                except Exception as e:
                    print(f'   ❌ Error: {str(e)}')
                
                time.sleep(0.5)
    
    except Exception as e:
        print(f'❌ Error accessing main sitemap: {str(e)}')
    
    return found_articles

def test_direct_category_access():
    """Test if articles are in category pages we haven't properly accessed"""
    print('\n📂 TESTING CATEGORY ACCESS WITH DIFFERENT METHODS')
    print('=' * 50)
    
    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # Our working categories
    categories = [
        'https://www.illawarramercury.com.au/www.illawarramercury.com.au',
        'https://www.illawarramercury.com.au/sport',
        'https://www.illawarramercury.com.au/news',
        'https://www.illawarramercury.com.au/local-news',
        'https://www.illawarramercury.com.au/politics',
    ]
    
    found_articles = []
    
    for category in categories:
        print(f'\n📂 Testing category: {category}')
        
        # Try different URL formats
        test_urls = [
            category,
            category + '/',
            category + '/page/1/',
            category + '?page=1',
        ]
        
        for test_url in test_urls:
            try:
                print(f'   🔗 Trying: {test_url}')
                response = requests.get(test_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for article links with different patterns
                    article_links = set()
                    
                    # Pattern 1: Direct story links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href:
                            if not href.startswith('http'):
                                href = 'https://www.illawarramercury.com.au' + href
                            article_links.add(href)
                    
                    # Pattern 2: Links in article containers
                    for article in soup.find_all(['article', 'div'], class_=re.compile(r'article|story|post')):
                        for link in article.find_all('a', href=True):
                            href = link['href']
                            if '/story/' in href:
                                if not href.startswith('http'):
                                    href = 'https://www.illawarramercury.com.au' + href
                                article_links.add(href)
                    
                    if article_links:
                        print(f'   ✅ Found {len(article_links)} articles')
                        
                        # Check for targets
                        for link in article_links:
                            for target_id in target_ids:
                                if target_id in link:
                                    print(f'   🎯 FOUND TARGET: {target_id} in {link}')
                                    found_articles.append((target_id, link))
                        
                        # Show sample IDs
                        sample_ids = []
                        for link in list(article_links)[:5]:
                            match = re.search(r'/story/(\d+)/', link)
                            if match:
                                sample_ids.append(int(match.group(1)))
                        if sample_ids:
                            print(f'   📊 Sample IDs: {min(sample_ids)}-{max(sample_ids)}')
                        
                        break  # Found working URL format
                    else:
                        print(f'   📄 No articles found')
                else:
                    print(f'   ❌ Status: {response.status_code}')
            except Exception as e:
                print(f'   ❌ Error: {str(e)}')
            
            time.sleep(0.5)
    
    return found_articles

def main():
    print('🔍 ARCHIVE AND HISTORICAL CONTENT DISCOVERY')
    print('=' * 60)
    
    all_found = []
    
    # Analyze story ID patterns
    min_recent, max_recent = analyze_story_id_patterns()
    
    # Test archive patterns
    archive_found = test_archive_patterns()
    all_found.extend(archive_found)
    
    # Check comprehensive sitemaps
    sitemap_found = check_comprehensive_sitemaps()
    all_found.extend(sitemap_found)
    
    # Test direct category access
    category_found = test_direct_category_access()
    all_found.extend(category_found)
    
    print('\n' + '=' * 60)
    print('📊 ARCHIVE DISCOVERY RESULTS')
    print('=' * 60)
    
    if all_found:
        unique_found = list(set(all_found))
        print(f'🎯 Found {len(unique_found)} unique target articles:')
        for target_id, url in unique_found:
            print(f'   • {target_id}: {url}')
        
        print('\n✅ SUCCESS: Located missing articles!')
        print('💡 These can now be integrated into the main search system.')
    else:
        print('❌ No target articles found in archive analysis')
        print('\n🤔 The articles exist (direct URLs work) but are not discoverable through:')
        print('   • Current RSS feeds')
        print('   • Sitemap indexes')
        print('   • Category navigation')
        print('   • Archive patterns')
        print('\n💡 This suggests:')
        print('   • Articles may be cached/indexed separately')
        print('   • May require search functionality to find')
        print('   • Could be in JavaScript-rendered sections')
        print('   • Might need specialized scraping approach')

if __name__ == "__main__":
    main()
