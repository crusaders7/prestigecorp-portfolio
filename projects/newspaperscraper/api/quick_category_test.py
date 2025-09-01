#!/usr/bin/env python3
"""
Quick category discovery for Illawarra Mercury
"""

import requests
from bs4 import BeautifulSoup
import time


def quick_category_test():
    """Quick test of common category URLs"""

    base_url = "https://www.illawarramercury.com.au"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive'
    }

    # Test categories based on common news site structures
    test_categories = [
        # Current categories
        "",  # Homepage
        "/news/",
        "/sport/",
        "/business/",
        "/news/local-news/",
        "/news/politics/",

        # Additional categories to test
        "/news/breaking-news/",
        "/news/crime/",
        "/news/health/",
        "/news/education/",
        "/news/environment/",
        "/lifestyle/",
        "/entertainment/",
        "/opinion/",
        "/property/",
        "/community/",
        "/weather/",

        # Regional categories
        "/wollongong/",
        "/shellharbour/",
        "/shoalhaven/",
        "/kiama/",
        "/illawarra/",
        "/regional/",

        # Sport subcategories
        "/sport/nrl/",
        "/sport/afl/",
        "/sport/football/",
        "/sport/rugby-league/",
        "/sport/cricket/",

        # Lifestyle subcategories
        "/lifestyle/food/",
        "/lifestyle/travel/",
        "/lifestyle/health/",
    ]

    working_categories = []
    print("🔍 Testing category URLs...")

    for category in test_categories:
        test_url = base_url + category
        try:
            response = requests.get(test_url, headers=headers, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                # Count story links
                story_links = soup.find_all(
                    'a', href=lambda x: x and '/story/' in x)
                article_count = len(story_links)

                if article_count > 0:
                    working_categories.append(
                        (category, test_url, article_count))
                    print(
                        f"✅ {category or 'homepage':<20} - {article_count:>3} articles")
                else:
                    print(f"⚠️  {category or 'homepage':<20} - No articles")
            else:
                print(
                    f"❌ {category or 'homepage':<20} - Status {response.status_code}")

        except Exception as e:
            print(f"❌ {category or 'homepage':<20} - Error: {str(e)[:30]}...")

        time.sleep(0.3)  # Small delay

    print(f"\n📊 RESULTS - Found {len(working_categories)} working categories:")
    print("-" * 60)

    # Sort by article count
    working_categories.sort(key=lambda x: x[2], reverse=True)

    total_articles = 0
    for category, url, count in working_categories:
        total_articles += count
        print(f"{category or 'homepage':<25} {count:>3} articles - {url}")

    print(f"\nTotal potential articles: {total_articles}")

    # Generate updated category list
    print(f"\n🚀 UPDATED CATEGORY LIST FOR search.py:")
    print("=" * 60)
    print("category_urls = [")

    # Include all working categories with at least 5 articles
    for category, url, count in working_categories:
        if count >= 5:  # Only categories with decent content
            print(
                f'    "{url}",  # {category or "homepage"} - {count} articles')

    print("]")

    return working_categories


if __name__ == "__main__":
    quick_category_test()
