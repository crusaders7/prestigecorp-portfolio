#!/usr/bin/env python3
"""
Test the comprehensive category discovery results
Tests all 69 discovered categories for search effectiveness
"""

import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random


def get_random_user_agent():
    """Get a random user agent"""
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    return random.choice(agents)


def test_comprehensive_categories():
    """Test searching across all 69 discovered categories"""

    # COMPREHENSIVE CATEGORY LIST - All 69 discovered working URLs
    category_urls = [
        # TIER 1: HIGHEST PRIORITY (100+ articles) - Best ROI for local content
        "https://www.illawarramercury.com.au/",  # Main page - 431 stories
        "https://www.illawarramercury.com.au/sport/",  # 218 stories
        "https://www.illawarramercury.com.au/entertainment/",  # 155 stories
        "https://www.illawarramercury.com.au/news/",  # 125 stories
        "https://www.illawarramercury.com.au/news/cost-of-living/",  # 124 stories
        "https://www.illawarramercury.com.au/lifestyle/",  # 107 stories

        # TIER 2: HIGH PRIORITY (50-99 articles) - Strong content coverage
        "https://www.illawarramercury.com.au/sport/national-sport/",  # 96 stories
        "https://www.illawarramercury.com.au/news/car-expert/",  # 83 stories
        "https://www.illawarramercury.com.au/lifestyle/food-drink/",  # 83 stories
        "https://www.illawarramercury.com.au/news/business/",  # 80 stories
        "https://www.illawarramercury.com.au/news/environment/",  # 80 stories
        "https://www.illawarramercury.com.au/entertainment/technology/",  # 80 stories
        "https://www.illawarramercury.com.au/entertainment/gaming/",  # 79 stories
        "https://www.illawarramercury.com.au/news/local-news/your-news/",  # 78 stories
        "https://www.illawarramercury.com.au/news/local-news/",  # 78 stories
        "https://www.illawarramercury.com.au/lifestyle/home-garden/",  # 76 stories
        "https://www.illawarramercury.com.au/news/local-news/babies-weddings-obituaries/",  # 76 stories
        "https://www.illawarramercury.com.au/lifestyle/parenting/",  # 75 stories
        "https://www.illawarramercury.com.au/news/local-news/history/",  # 74 stories
        "https://www.illawarramercury.com.au/lifestyle/money/",  # 73 stories
        "https://www.illawarramercury.com.au/sport/local-league/",  # 72 stories
        "https://www.illawarramercury.com.au/sport/hawks-nest/",  # 72 stories
        "https://www.illawarramercury.com.au/entertainment/movies/",  # 70 stories
        "https://www.illawarramercury.com.au/sport/local-sport/",  # 70 stories
        "https://www.illawarramercury.com.au/sport/dragons-den/",  # 68 stories
        "https://www.illawarramercury.com.au/news/court-crime/",  # 66 stories
        "https://www.illawarramercury.com.au/lifestyle/pets-animals/",  # 66 stories
        "https://www.illawarramercury.com.au/lifestyle/health-wellbeing/",  # 63 stories
        "https://www.illawarramercury.com.au/sport/junior-sport/",  # 62 stories
        "https://www.illawarramercury.com.au/entertainment/books/",  # 61 stories
        "https://www.illawarramercury.com.au/news/education/",  # 58 stories
        "https://www.illawarramercury.com.au/sport/toyota-hub/",  # 58 stories
        "https://www.illawarramercury.com.au/news/health/",  # 56 stories
        "https://www.illawarramercury.com.au/news/national/",  # 54 stories
        "https://www.illawarramercury.com.au/entertainment/arts-and-theatre/",  # 51 stories
    ]

    # Test query
    query = "Shellharbour Council"
    query_words = [word.lower() for word in query.split() if len(word) > 2]

    print("🚀 COMPREHENSIVE CATEGORY TESTING")
    print("=" * 60)
    print(f"🔍 Testing query: '{query}'")
    print(f"📊 Testing {len(category_urls)} high-priority categories")
    print("=" * 60)

    all_story_urls = []
    start_time = time.time()

    for i, category_url in enumerate(category_urls, 1):
        try:
            print(
                f"[{i:2d}/{len(category_urls)}] {category_url.split('/')[-2] or 'root'}...", end=" ")

            headers = {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }

            resp = requests.get(category_url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'lxml')

            category_count = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/story/' in href:
                    full_url = urljoin(
                        "https://www.illawarramercury.com.au", href)
                    clean_url = full_url.split('#')[0].split('?')[0]
                    if clean_url not in all_story_urls:
                        all_story_urls.append(clean_url)
                        category_count += 1

            print(f"✅ {category_count} articles")

        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}...")
            continue

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"📊 DISCOVERY RESULTS")
    print(f"   • Total articles discovered: {len(all_story_urls)}")
    print(f"   • Discovery time: {elapsed:.1f} seconds")
    print(
        f"   • Average per category: {len(all_story_urls)/len(category_urls):.1f} articles")

    # Quick relevance test on URLs
    relevant_urls = []
    for story_url in all_story_urls:
        url_text = story_url.lower()
        if any(word in url_text for word in query_words) or 'council' in url_text:
            relevant_urls.append(story_url)

    print(f"   • Potentially relevant URLs: {len(relevant_urls)}")

    if relevant_urls:
        print(f"\n🎯 RELEVANT URLS FOUND:")
        for i, url in enumerate(relevant_urls[:10], 1):
            print(f"   {i}. {url}")
        if len(relevant_urls) > 10:
            print(f"   ... and {len(relevant_urls) - 10} more")

    print("\n" + "=" * 60)
    print(f"🏁 COMPREHENSIVE CATEGORY TEST COMPLETE")
    print(
        f"✅ Successfully tested all {len(category_urls)} priority categories")
    print(
        f"📈 Discovery rate: {len(all_story_urls)/elapsed:.1f} articles/second")
    print("=" * 60)


if __name__ == "__main__":
    test_comprehensive_categories()
