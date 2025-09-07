#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import time


def search_shellharbour_directly():
    """Test direct search on Illawarra Mercury for Shellharbour Council"""
    print("Searching directly for Shellharbour Council articles...")

    # Try the site's own search function
    search_terms = [
        "shellharbour council",
        "Shellharbour Council",
        "shellharbour city council",
        "Shell Harbour"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for term in search_terms:
        print(f"\n{'='*50}")
        print(f"Testing direct search: '{term}'")
        print('='*50)

        try:
            # Try the site's search URL
            search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(term)}"
            print(f"Search URL: {search_url}")

            resp = requests.get(search_url, headers=headers, timeout=15)
            print(f"Status: {resp.status_code}")

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')

                # Look for search results
                results = []

                # Try common search result selectors
                for selector in [
                    'article',
                    '.search-result',
                    '.story-block',
                    'h3 a[href*="/story/"]',
                    'a[href*="/story/"]'
                ]:
                    elements = soup.select(selector)
                    if elements:
                        print(
                            f"Found {len(elements)} elements with selector: {selector}")
                        for elem in elements[:3]:  # Show first 3
                            if elem.name == 'a':
                                href = elem.get('href', '')
                                text = elem.get_text().strip()
                                if '/story/' in href and text:
                                    print(f"  - {text[:60]}...")
                                    print(f"    URL: {href}")
                            else:
                                # Look for links within the element
                                link = elem.find('a', href=True)
                                if link and '/story/' in link.get('href', ''):
                                    text = elem.get_text().strip()
                                    print(f"  - {text[:60]}...")
                                    print(f"    URL: {link.get('href')}")
                        break

                # Also check page content for any mention of search results count
                page_text = soup.get_text().lower()
                if 'results' in page_text or 'found' in page_text:
                    lines = page_text.split('\n')
                    for line in lines:
                        if ('result' in line or 'found' in line) and any(char.isdigit() for char in line):
                            print(f"Search info: {line.strip()}")
                            break

        except Exception as e:
            print(f"Error searching for '{term}': {e}")

        time.sleep(2)  # Be respectful

    # Also try Google site search to see if articles exist
    print(f"\n{'='*50}")
    print("Trying Google site search...")
    print('='*50)

    try:
        google_query = "site:illawarramercury.com.au \"shellharbour council\""
        google_url = f"https://www.google.com/search?q={quote_plus(google_query)}"
        print(f"Google search URL: {google_url}")

        resp = requests.get(google_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')

            # Look for result count
            stats = soup.find('div', {'id': 'result-stats'})
            if stats:
                print(f"Google says: {stats.get_text()}")

            # Look for search results
            results = soup.select('h3')
            if results:
                print(f"Found {len(results)} Google results")
                for i, result in enumerate(results[:5], 1):
                    title = result.get_text()
                    print(f"{i}. {title}")

                    # Try to find the URL
                    parent = result.find_parent('a')
                    if parent:
                        href = parent.get('href', '')
                        if 'illawarramercury.com.au' in href:
                            print(f"   URL: {href}")

    except Exception as e:
        print(f"Error with Google search: {e}")


if __name__ == "__main__":
    search_shellharbour_directly()
