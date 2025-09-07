#!/usr/bin/env python3
"""
DEEP RSS PAGINATION SEARCH
Uses discovered pagination to search deep into RSS feeds for missing articles
"""

import requests
from bs4 import BeautifulSoup
import re
import time


def deep_rss_pagination_search(target_ids=None, max_pages=20):
    """Search deep into RSS pagination for target articles"""
    if target_ids is None:
        target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']

    print("🔍 DEEP RSS PAGINATION SEARCH")
    print("=" * 50)
    print(f"🎯 Searching for target IDs: {target_ids}")
    print(f"📄 Testing up to {max_pages} pages per feed")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # RSS feeds that support pagination
    rss_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/entertainment/rss.xml',
        'https://www.illawarramercury.com.au/lifestyle/rss.xml',
    ]

    found_targets = {}
    all_articles_scanned = 0

    for feed_url in rss_feeds:
        print(f"\n📡 Deep scanning: {feed_url}")
        feed_articles = 0
        feed_targets = []

        for page in range(1, max_pages + 1):
            try:
                # Test different pagination formats
                page_urls = [
                    f"{feed_url}?page={page}",
                    f"{feed_url}?p={page}",
                    f"{feed_url}&page={page}",
                ]

                page_found = False
                for page_url in page_urls:
                    try:
                        response = requests.get(
                            page_url, headers=headers, timeout=15)

                        if response.status_code == 200:
                            # Check if it's valid XML
                            if response.text.strip().startswith('<?xml'):
                                soup = BeautifulSoup(response.content, 'xml')
                                items = soup.find_all(['item', 'entry'])

                                if items:
                                    page_found = True
                                    feed_articles += len(items)

                                    # Extract story IDs and check for targets
                                    page_story_ids = []
                                    for item in items:
                                        link_elem = item.find(['link'])
                                        if link_elem:
                                            link = link_elem.get_text(
                                                strip=True) if link_elem.string else link_elem.get('href', '')
                                            story_match = re.search(
                                                r'/story/(\d+)/', link)
                                            if story_match:
                                                story_id = story_match.group(1)
                                                page_story_ids.append(story_id)

                                                # Check if it's a target
                                                if story_id in target_ids:
                                                    title_elem = item.find(
                                                        ['title'])
                                                    title = title_elem.get_text(
                                                        strip=True) if title_elem else "No title"

                                                    target_info = {
                                                        'story_id': story_id,
                                                        'title': title,
                                                        'url': link,
                                                        'feed': feed_url,
                                                        'page': page,
                                                        'page_url': page_url
                                                    }

                                                    feed_targets.append(
                                                        target_info)
                                                    found_targets[story_id] = target_info

                                                    print(
                                                        f"   🎯 FOUND TARGET on page {page}: {story_id} - {title[:50]}...")

                                    if page_story_ids:
                                        id_range = f"{min(page_story_ids)}-{max(page_story_ids)}"
                                        print(
                                            f"   📄 Page {page}: {len(items)} items (IDs: {id_range})")
                                    else:
                                        print(
                                            f"   📄 Page {page}: {len(items)} items (no story IDs found)")

                                    break  # Found working pagination format
                                else:
                                    # Empty page - might be end of content
                                    print(
                                        f"   📄 Page {page}: Empty page, end of content")
                                    page_found = False
                                    break
                    except Exception as e:
                        continue

                if not page_found:
                    if page == 1:
                        print(f"   ❌ Feed not accessible")
                    else:
                        print(f"   📄 End of pagination at page {page}")
                    break

                time.sleep(0.3)  # Rate limiting

            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break

        all_articles_scanned += feed_articles

        if feed_targets:
            print(
                f"   ✅ Feed summary: {feed_articles} articles scanned, {len(feed_targets)} targets found")
        else:
            print(
                f"   📊 Feed summary: {feed_articles} articles scanned, no targets found")

    return found_targets, all_articles_scanned


def comprehensive_rss_article_discovery(query="shellharbour council", max_pages=15):
    """Comprehensive article discovery using deep RSS pagination"""
    print(f"\n🔍 COMPREHENSIVE RSS ARTICLE DISCOVERY")
    print(f"Query: '{query}' | Max pages: {max_pages}")
    print("=" * 60)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    query_terms = query.lower().split()

    all_relevant_articles = []
    total_articles_scanned = 0

    rss_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
    ]

    for feed_url in rss_feeds:
        print(f"\n📡 Comprehensive scan: {feed_url}")
        feed_articles = 0
        feed_relevant = 0

        for page in range(1, max_pages + 1):
            try:
                page_url = f"{feed_url}?page={page}"
                response = requests.get(page_url, headers=headers, timeout=15)

                if response.status_code == 200 and response.text.strip().startswith('<?xml'):
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all(['item', 'entry'])

                    if not items:
                        print(f"   📄 Page {page}: End of content")
                        break

                    feed_articles += len(items)
                    page_relevant = 0

                    for item in items:
                        # Extract article details
                        title_elem = item.find(['title'])
                        link_elem = item.find(['link'])
                        desc_elem = item.find(['description', 'summary'])

                        if title_elem and link_elem:
                            title = title_elem.get_text(strip=True)
                            link = link_elem.get_text(
                                strip=True) if link_elem.string else link_elem.get('href', '')
                            description = desc_elem.get_text(
                                strip=True) if desc_elem else ""

                            # Check relevance
                            search_text = (
                                title + " " + description + " " + link).lower()
                            relevance_score = 0

                            for term in query_terms:
                                if term in search_text:
                                    relevance_score += 1

                            if relevance_score > 0:
                                # Extract story ID
                                story_id = ""
                                story_match = re.search(r'/story/(\d+)/', link)
                                if story_match:
                                    story_id = story_match.group(1)

                                article_data = {
                                    'title': title,
                                    'url': link,
                                    'description': description,
                                    'story_id': story_id,
                                    'relevance_score': relevance_score,
                                    'feed': feed_url,
                                    'page': page,
                                    'source': 'deep_rss_pagination'
                                }

                                all_relevant_articles.append(article_data)
                                page_relevant += 1
                                feed_relevant += 1

                    if page_relevant > 0:
                        print(
                            f"   📄 Page {page}: {len(items)} items, {page_relevant} relevant")
                    else:
                        print(f"   📄 Page {page}: {len(items)} items")
                else:
                    print(f"   📄 Page {page}: End of pagination")
                    break

                time.sleep(0.3)

            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break

        total_articles_scanned += feed_articles
        print(
            f"   📊 Feed summary: {feed_articles} total, {feed_relevant} relevant articles")

    # Sort by relevance
    all_relevant_articles.sort(
        key=lambda x: x['relevance_score'], reverse=True)

    return all_relevant_articles, total_articles_scanned


def main():
    """Main execution function"""
    print("🚀 DEEP RSS PAGINATION ANALYSIS")
    print("=" * 70)

    # Search for specific target articles
    print("\n📊 PHASE 1: TARGET ARTICLE SEARCH")
    found_targets, scanned_count = deep_rss_pagination_search(max_pages=30)

    print(f"\n📊 TARGET SEARCH RESULTS:")
    print(f"   🎯 Targets found: {len(found_targets)}/5")
    print(f"   📰 Articles scanned: {scanned_count}")

    if found_targets:
        print(f"\n🎯 FOUND TARGET ARTICLES:")
        for story_id, info in found_targets.items():
            print(f"   ✅ {story_id}: {info['title'][:60]}...")
            print(f"      📡 Feed: {info['feed']}")
            print(f"      📄 Page: {info['page']}")
            print(f"      🔗 URL: {info['url']}")
            print()

    # Comprehensive relevance search
    print("\n📊 PHASE 2: COMPREHENSIVE RELEVANCE SEARCH")
    relevant_articles, total_scanned = comprehensive_rss_article_discovery(
        "shellharbour council", max_pages=20)

    print(f"\n📊 COMPREHENSIVE SEARCH RESULTS:")
    print(f"   📰 Total articles scanned: {total_scanned}")
    print(f"   🎯 Relevant articles found: {len(relevant_articles)}")

    if relevant_articles:
        print(f"\n📝 TOP RELEVANT ARTICLES:")
        for i, article in enumerate(relevant_articles[:10], 1):
            print(
                f"   {i}. Score {article['relevance_score']}: {article['title'][:60]}...")
            if article['story_id']:
                print(
                    f"      ID: {article['story_id']} | Page: {article['page']}")
            print(f"      URL: {article['url']}")
            print()

    print("✅ DEEP RSS PAGINATION ANALYSIS COMPLETE!")
    print(
        f"💡 RSS pagination provides access to {total_scanned} total articles!")


if __name__ == "__main__":
    main()
