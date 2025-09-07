#!/usr/bin/env python3
"""
Discover available categories on Illawarra Mercury website
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time


def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'


def discover_categories():
    """Discover all available categories on the Illawarra Mercury website"""

    base_url = "https://www.illawarramercury.com.au"
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }

    print("🔍 Discovering categories on Illawarra Mercury...")

    try:
        # Get the homepage
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Look for navigation menus and category links
        categories = set()

        # Method 1: Look for navigation menus
        nav_elements = soup.find_all(
            ['nav', 'ul', 'div'], class_=re.compile(r'nav|menu|category', re.I))

        print("\n📋 Found navigation elements:")
        for nav in nav_elements:
            nav_class = nav.get('class', [])
            nav_id = nav.get('id', '')
            print(f"  - {nav.name} with class: {nav_class}, id: {nav_id}")

            # Extract links from navigation
            for link in nav.find_all('a', href=True):
                href = link['href']
                text = link.get_text().strip()

                if href.startswith('/') and len(text) > 0:
                    full_url = urljoin(base_url, href)
                    if any(keyword in href.lower() for keyword in ['news', 'sport', 'business', 'lifestyle', 'entertainment', 'opinion', 'community', 'local']):
                        categories.add((text, full_url))

        # Method 2: Look for specific category patterns in all links
        print("\n🔗 Scanning all links for category patterns...")
        all_links = soup.find_all('a', href=True)

        category_patterns = [
            r'/news/?$',
            r'/sport/?$',
            r'/business/?$',
            r'/lifestyle/?$',
            r'/entertainment/?$',
            r'/opinion/?$',
            r'/community/?$',
            r'/local/?$',
            r'/politics/?$',
            r'/health/?$',
            r'/education/?$',
            r'/property/?$',
            r'/technology/?$',
            r'/environment/?$',
            r'/crime/?$',
            r'/weather/?$',
            r'/breaking-news/?$',
            r'/local-news/?$',
            r'/regional/?$',
            r'/illawarra/?$',
            r'/wollongong/?$',
            r'/shellharbour/?$',
            r'/shoalhaven/?$',
            r'/kiama/?$'
        ]

        for link in all_links:
            href = link['href']
            text = link.get_text().strip()

            if href.startswith('/'):
                for pattern in category_patterns:
                    if re.search(pattern, href):
                        full_url = urljoin(base_url, href)
                        categories.add((text, full_url))

        # Method 3: Try common category URLs directly
        print("\n🎯 Testing common category URLs...")
        common_categories = [
            '/news/',
            '/news/local-news/',
            '/news/breaking-news/',
            '/news/politics/',
            '/news/business/',
            '/news/health/',
            '/news/education/',
            '/news/environment/',
            '/news/crime/',
            '/sport/',
            '/sport/football/',
            '/sport/rugby-league/',
            '/sport/cricket/',
            '/sport/basketball/',
            '/business/',
            '/lifestyle/',
            '/lifestyle/food/',
            '/lifestyle/travel/',
            '/entertainment/',
            '/opinion/',
            '/community/',
            '/property/',
            '/weather/',
            '/illawarra/',
            '/wollongong/',
            '/shellharbour/',
            '/shoalhaven/',
            '/kiama/',
            '/regional/',
            '/local/'
        ]

        working_categories = []
        for cat_path in common_categories:
            test_url = base_url + cat_path
            try:
                test_response = requests.get(
                    test_url, headers=headers, timeout=10)
                if test_response.status_code == 200:
                    # Quick check if it has articles
                    test_soup = BeautifulSoup(test_response.content, 'lxml')
                    story_links = test_soup.find_all(
                        'a', href=re.compile(r'/story/'))
                    if story_links:
                        working_categories.append(
                            (cat_path, test_url, len(story_links)))
                        print(f"  ✅ {test_url} - {len(story_links)} articles")
                    else:
                        print(f"  ⚠️  {test_url} - No articles found")
                else:
                    print(
                        f"  ❌ {test_url} - Status {test_response.status_code}")
            except Exception as e:
                print(f"  ❌ {test_url} - Error: {e}")

            time.sleep(0.5)  # Be respectful

        print(f"\n📊 DISCOVERY RESULTS:")
        print(f"Found {len(categories)} categories from navigation")
        print(f"Found {len(working_categories)} working category URLs")

        print(f"\n🔗 Navigation Categories:")
        for text, url in sorted(categories):
            print(f"  • {text}: {url}")

        print(f"\n✅ Working Category URLs (with article counts):")
        for path, url, count in sorted(working_categories, key=lambda x: x[2], reverse=True):
            print(f"  • {path} ({count} articles): {url}")

        # Generate updated category list
        print(f"\n🚀 RECOMMENDED CATEGORY UPDATE:")
        print("Add these to your category_urls list:")

        # Combine current categories with discovered ones
        current_categories = [
            "https://www.illawarramercury.com.au",
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/news/business/",
            "https://www.illawarramercury.com.au/news/local-news/",
            "https://www.illawarramercury.com.au/news/politics/"
        ]

        recommended = set(current_categories)
        for path, url, count in working_categories:
            if count > 5:  # Only include categories with decent article counts
                recommended.add(url)

        print("category_urls = [")
        for url in sorted(recommended):
            print(f'    "{url}",')
        print("]")

        return list(recommended)

    except Exception as e:
        print(f"❌ Error discovering categories: {e}")
        return []


if __name__ == "__main__":
    discover_categories()
