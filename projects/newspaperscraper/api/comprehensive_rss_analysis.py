#!/usr/bin/env python3
"""
COMPREHENSIVE RSS FEED ANALYSIS
Discover and analyze all available RSS feeds for enhanced article discovery
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import xml.etree.ElementTree as ET


def discover_all_rss_feeds():
    """Discover all available RSS feeds on the site"""
    print("🔍 DISCOVERING ALL RSS FEEDS")
    print("=" * 50)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    discovered_feeds = set()

    # Method 1: Check robots.txt for feed references
    print("\n📋 Checking robots.txt...")
    try:
        response = requests.get(
            'https://www.illawarramercury.com.au/robots.txt', headers=headers)
        if response.status_code == 200:
            content = response.text
            print(f"   ✅ robots.txt accessible ({len(content)} chars)")

            # Look for RSS/feed references
            feed_urls = re.findall(
                r'https://[^\s]+(?:rss|feed|xml)[^\s]*', content, re.IGNORECASE)
            if feed_urls:
                print(
                    f"   📡 Found {len(feed_urls)} feed references in robots.txt:")
                for feed_url in feed_urls:
                    print(f"      • {feed_url}")
                    discovered_feeds.add(feed_url)
    except Exception as e:
        print(f"   ❌ Error accessing robots.txt: {e}")

    # Method 2: Check main page for feed links
    print("\n🏠 Checking main page for feed links...")
    try:
        response = requests.get(
            'https://www.illawarramercury.com.au/', headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for RSS link tags
            rss_links = soup.find_all(
                'link', {'type': re.compile(r'application/(rss|atom)\+xml', re.I)})
            if rss_links:
                print(f"   📡 Found {len(rss_links)} RSS link tags:")
                for link in rss_links:
                    href = link.get('href')
                    title = link.get('title', 'No title')
                    if href:
                        if not href.startswith('http'):
                            href = 'https://www.illawarramercury.com.au' + href
                        print(f"      • {title}: {href}")
                        discovered_feeds.add(href)

            # Look for feed links in the page content
            all_links = soup.find_all('a', href=True)
            feed_links = [link['href'] for link in all_links if 'rss' in link['href'].lower(
            ) or 'feed' in link['href'].lower()]
            if feed_links:
                print(f"   📡 Found {len(feed_links)} feed links in content:")
                for link in feed_links:
                    if not link.startswith('http'):
                        link = 'https://www.illawarramercury.com.au' + link
                    print(f"      • {link}")
                    discovered_feeds.add(link)
    except Exception as e:
        print(f"   ❌ Error checking main page: {e}")

    # Method 3: Test common RSS URL patterns
    print("\n🧪 Testing common RSS URL patterns...")
    common_patterns = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/feed/',
        'https://www.illawarramercury.com.au/rss/',
        'https://www.illawarramercury.com.au/feeds/all.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/politics/rss.xml',
        'https://www.illawarramercury.com.au/business/rss.xml',
        'https://www.illawarramercury.com.au/entertainment/rss.xml',
        'https://www.illawarramercury.com.au/lifestyle/rss.xml',
        'https://www.illawarramercury.com.au/local-news/rss.xml',
        'https://www.illawarramercury.com.au/breaking-news/rss.xml',
        'https://www.illawarramercury.com.au/latest/rss.xml',
        'https://www.illawarramercury.com.au/feeds/news.xml',
        'https://www.illawarramercury.com.au/feeds/sport.xml',
        'https://www.illawarramercury.com.au/feeds/latest.xml',
        'https://www.illawarramercury.com.au/atom.xml',
        'https://www.illawarramercury.com.au/index.xml',
    ]

    working_feeds = []
    for pattern in common_patterns:
        try:
            response = requests.get(pattern, headers=headers, timeout=10)
            if response.status_code == 200:
                # Check if it's actually XML/RSS content
                content_type = response.headers.get('content-type', '').lower()
                if 'xml' in content_type or response.text.strip().startswith('<?xml'):
                    print(f"   ✅ Working: {pattern}")
                    working_feeds.append(pattern)
                    discovered_feeds.add(pattern)
                else:
                    print(f"   ⚠️ Not XML: {pattern}")
            else:
                print(f"   ❌ {response.status_code}: {pattern}")
        except Exception as e:
            print(f"   ❌ Error: {pattern}")

        time.sleep(0.3)  # Rate limiting

    return list(discovered_feeds), working_feeds


def analyze_rss_feed_content(feed_url):
    """Analyze the content and structure of an RSS feed"""
    print(f"\n📡 ANALYZING: {feed_url}")
    print("-" * 60)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(feed_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"   ❌ Status: {response.status_code}")
            return {}

        # Parse as XML
        try:
            soup = BeautifulSoup(response.content, 'xml')
        except:
            soup = BeautifulSoup(response.content, 'html.parser')

        analysis = {
            'url': feed_url,
            'size': len(response.content),
            'articles': [],
            'story_ids': [],
            'categories': set(),
            'date_range': {'oldest': None, 'newest': None},
            'total_items': 0,
            'shellharbour_articles': [],
            'council_articles': []
        }

        # Extract articles/items
        items = soup.find_all(['item', 'entry'])
        analysis['total_items'] = len(items)

        print(f"   📊 Found {len(items)} items ({analysis['size']} bytes)")

        for item in items:
            article = {}

            # Extract title
            title_elem = item.find(['title'])
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)

            # Extract link/URL
            link_elem = item.find(['link'])
            if link_elem:
                link = link_elem.get_text(
                    strip=True) if link_elem.string else link_elem.get('href', '')
                article['url'] = link

                # Extract story ID
                story_match = re.search(r'/story/(\d+)/', link)
                if story_match:
                    story_id = story_match.group(1)
                    article['story_id'] = story_id
                    analysis['story_ids'].append(int(story_id))

            # Extract description/content
            desc_elem = item.find(['description', 'summary', 'content'])
            if desc_elem:
                article['description'] = desc_elem.get_text(strip=True)

            # Extract publication date
            date_elem = item.find(['pubDate', 'published', 'updated'])
            if date_elem:
                article['pub_date'] = date_elem.get_text(strip=True)

            # Extract category
            category_elem = item.find(['category'])
            if category_elem:
                category = category_elem.get_text(strip=True)
                article['category'] = category
                analysis['categories'].add(category)

            # Check for Shellharbour content
            text_content = (article.get('title', '') + ' ' +
                            article.get('description', '')).lower()
            if 'shellharbour' in text_content:
                analysis['shellharbour_articles'].append(article)
            if 'council' in text_content:
                analysis['council_articles'].append(article)

            analysis['articles'].append(article)

        # Analyze story ID range
        if analysis['story_ids']:
            analysis['id_range'] = {
                'min': min(analysis['story_ids']),
                'max': max(analysis['story_ids']),
                'span': max(analysis['story_ids']) - min(analysis['story_ids'])
            }
            print(
                f"   📈 Story ID range: {analysis['id_range']['min']} - {analysis['id_range']['max']} (span: {analysis['id_range']['span']})")

        # Show categories
        if analysis['categories']:
            print(
                f"   📂 Categories: {', '.join(list(analysis['categories'])[:5])}{'...' if len(analysis['categories']) > 5 else ''}")

        # Show Shellharbour matches
        if analysis['shellharbour_articles']:
            print(
                f"   🎯 Shellharbour articles: {len(analysis['shellharbour_articles'])}")
            for article in analysis['shellharbour_articles'][:3]:
                print(f"      • {article.get('title', 'No title')[:60]}...")

        # Show council matches
        if analysis['council_articles']:
            print(
                f"   🏛️ Council articles: {len(analysis['council_articles'])}")
            for article in analysis['council_articles'][:3]:
                print(f"      • {article.get('title', 'No title')[:60]}...")

        return analysis

    except Exception as e:
        print(f"   ❌ Error analyzing feed: {e}")
        return {}


def enhanced_rss_search(query="shellharbour council"):
    """Enhanced search using all discovered RSS feeds"""
    print(f"\n🔍 ENHANCED RSS SEARCH for '{query}'")
    print("=" * 60)

    query_terms = query.lower().split()
    all_results = []

    # Discover all feeds
    all_feeds, working_feeds = discover_all_rss_feeds()

    print(f"\n📡 Found {len(working_feeds)} working RSS feeds to search:")
    for feed in working_feeds:
        print(f"   • {feed}")

    # Search each working feed
    for feed_url in working_feeds:
        analysis = analyze_rss_feed_content(feed_url)

        if analysis and analysis['articles']:
            # Find relevant articles in this feed
            relevant_articles = []

            for article in analysis['articles']:
                relevance_score = 0
                search_text = (
                    article.get('title', '') + ' ' +
                    article.get('description', '') + ' ' +
                    article.get('url', '')
                ).lower()

                for term in query_terms:
                    if term in search_text:
                        relevance_score += 1

                if relevance_score > 0:
                    article['relevance_score'] = relevance_score
                    article['feed_source'] = feed_url
                    relevant_articles.append(article)

            if relevant_articles:
                print(
                    f"   🎯 Found {len(relevant_articles)} relevant articles in this feed")
                all_results.extend(relevant_articles)

    return all_results, working_feeds


def comprehensive_rss_discovery():
    """Comprehensive RSS discovery and analysis"""
    print("🚀 COMPREHENSIVE RSS FEED DISCOVERY & ANALYSIS")
    print("=" * 70)

    # Discovery phase
    results, working_feeds = enhanced_rss_search("shellharbour council")

    print(f"\n📊 RSS SEARCH SUMMARY")
    print("=" * 50)
    print(f"📡 Working RSS feeds discovered: {len(working_feeds)}")
    print(f"📰 Total relevant articles found: {len(results)}")

    if results:
        print(f"\n🎯 TOP RELEVANT ARTICLES FROM RSS:")
        # Sort by relevance score
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        for i, article in enumerate(results[:10], 1):
            print(
                f"\n   {i}. Score: {article.get('relevance_score', 0)} | {article.get('title', 'No title')[:60]}...")
            print(f"      URL: {article.get('url', 'No URL')}")
            print(f"      Feed: {article.get('feed_source', 'Unknown feed')}")
            if article.get('story_id'):
                print(f"      Story ID: {article['story_id']}")

    # Detailed analysis of each working feed
    print(f"\n📡 DETAILED FEED ANALYSIS")
    print("=" * 50)

    for feed_url in working_feeds:
        analysis = analyze_rss_feed_content(feed_url)
        if analysis:
            print(f"\n🔍 FEED: {feed_url}")
            print(f"   📊 Total items: {analysis['total_items']}")
            if analysis.get('id_range'):
                print(
                    f"   📈 ID range: {analysis['id_range']['min']} - {analysis['id_range']['max']}")
            print(
                f"   🎯 Shellharbour content: {len(analysis['shellharbour_articles'])} articles")
            print(
                f"   🏛️ Council content: {len(analysis['council_articles'])} articles")

    return results, working_feeds


def test_specific_story_ids_in_rss():
    """Test if our target story IDs appear in any RSS feeds"""
    print(f"\n🎯 TESTING TARGET STORY IDs IN RSS FEEDS")
    print("=" * 50)

    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']

    # Get working feeds
    _, working_feeds = discover_all_rss_feeds()

    found_targets = {}

    for feed_url in working_feeds:
        analysis = analyze_rss_feed_content(feed_url)

        if analysis and analysis['story_ids']:
            feed_story_ids = [str(sid) for sid in analysis['story_ids']]

            for target_id in target_ids:
                if target_id in feed_story_ids:
                    if target_id not in found_targets:
                        found_targets[target_id] = []
                    found_targets[target_id].append(feed_url)
                    print(f"   🎯 Found target {target_id} in {feed_url}")

    print(f"\n📊 TARGET ANALYSIS SUMMARY:")
    print(f"   🎯 Targets found in RSS: {len(found_targets)}/{len(target_ids)}")
    print(
        f"   ❌ Missing from RSS: {set(target_ids) - set(found_targets.keys())}")

    return found_targets


if __name__ == "__main__":
    # Run comprehensive analysis
    results, feeds = comprehensive_rss_discovery()

    # Test target story IDs
    target_analysis = test_specific_story_ids_in_rss()

    print(f"\n✅ COMPREHENSIVE RSS ANALYSIS COMPLETE!")
    print(
        f"💡 Discovered {len(feeds)} working RSS feeds with enhanced search capabilities")
