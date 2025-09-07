#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import time


def test_site_search():
    """Test using the site's own search function"""
    print("Testing Illawarra Mercury site search for 'shellharbour council'...")

    query = "shellharbour council"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}"
    print(f"Search URL: {search_url}")

    try:
        resp = requests.get(search_url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')

            # Save the HTML to see what we're working with
            with open('search_results.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("Saved search results to search_results.html")

            # Try to find search results
            search_results = []
            seen_urls = set()

            print("\nTrying different selectors...")

            # Try various selectors
            selectors_to_try = [
                'article a[href*="/story/"]',
                '.search-result a[href*="/story/"]',
                '.story-block a[href*="/story/"]',
                'h3 a[href*="/story/"]',
                'h2 a[href*="/story/"]',
                '.headline a[href*="/story/"]',
                '.title a[href*="/story/"]',
                'a[href*="/story/"]'
            ]

            for selector in selectors_to_try:
                links = soup.select(selector)
                print(f"Selector '{selector}': {len(links)} links")

                if links:
                    for link in links[:5]:  # Show first 5
                        href = link.get('href', '')
                        text = link.get_text().strip()
                        if '/story/' in href:
                            full_url = urljoin(
                                "https://www.illawarramercury.com.au", href)
                            clean_url = full_url.split('#')[0].split('?')[0]
                            if clean_url not in seen_urls:
                                search_results.append({
                                    'url': clean_url,
                                    'title': text,
                                    'selector': selector
                                })
                                seen_urls.add(clean_url)
                                print(f"  Found: {text[:50]}...")
                                print(f"    URL: {clean_url}")

                    if len(search_results) >= 10:
                        break

            print(f"\nTotal unique articles found: {len(search_results)}")

            # Test fetching a few articles to get full titles
            if search_results:
                print(f"\nTesting article fetching...")
                for i, result in enumerate(search_results[:3], 1):
                    try:
                        article_resp = requests.get(
                            result['url'], headers=headers, timeout=10)
                        if article_resp.status_code == 200:
                            article_soup = BeautifulSoup(
                                article_resp.content, 'lxml')
                            title_elem = article_soup.find('h1')
                            full_title = title_elem.get_text().strip() if title_elem else "No title"

                            date_elem = article_soup.find('time')
                            date = date_elem.get(
                                'datetime', '') if date_elem else ""

                            print(f"{i}. {full_title}")
                            print(f"   URL: {result['url']}")
                            if date:
                                print(f"   Date: {date}")
                            print()
                    except Exception as e:
                        print(f"Error fetching article {i}: {e}")

        else:
            print(f"Failed to fetch search results: {resp.status_code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_site_search()
