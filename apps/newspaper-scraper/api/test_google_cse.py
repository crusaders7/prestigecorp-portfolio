#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
import time


def test_google_custom_search():
    """Test using Google Custom Search API that the site uses"""
    print("Testing Google Custom Search API for Illawarra Mercury...")

    query = "shellharbour council"
    # Google Custom Search ID from the site's code
    cx = "012527284968046999840:zzi3qgsoibq"

    # Try the Google Custom Search API endpoint
    api_url = f"https://www.googleapis.com/customsearch/v1"

    params = {
        'q': query,
        'cx': cx,
        'key': '',  # Would need API key for official API
    }

    # Since we don't have an API key, let's try the older JSON API endpoint
    # that some sites use
    json_api_url = f"https://www.googleapis.com/customsearch/v1element?q={quote_plus(query)}&cx={cx}&callback=handleResponse"

    print(f"Trying JSON API: {json_api_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.illawarramercury.com.au/'
    }

    try:
        resp = requests.get(json_api_url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            content = resp.text
            print(f"Response length: {len(content)} characters")
            print(f"First 200 chars: {content[:200]}")

            # Look for article URLs
            if 'illawarramercury.com.au/story/' in content:
                print("Found story URLs in response!")

                # Try to extract URLs (basic approach)
                import re
                story_urls = re.findall(
                    r'https://www\.illawarramercury\.com\.au/story/[^"\']+', content)
                print(f"Found {len(story_urls)} story URLs:")

                for i, url in enumerate(story_urls[:10], 1):
                    print(f"{i}. {url}")
            else:
                print("No story URLs found in response")
        else:
            print(f"Failed: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Alternative: Try to mimic the site's search more closely
    print(f"\nTrying alternative approach...")

    # Let's try using a headless approach or see if there are other endpoints
    search_endpoints_to_try = [
        f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}&format=json",
        f"https://www.illawarramercury.com.au/api/search?q={quote_plus(query)}",
        f"https://www.illawarramercury.com.au/search/results?q={quote_plus(query)}",
    ]

    for endpoint in search_endpoints_to_try:
        try:
            print(f"Trying: {endpoint}")
            resp = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200 and len(resp.text) > 100:
                print(f"  Response length: {len(resp.text)}")
                if 'story' in resp.text.lower():
                    print(f"  Contains 'story' - might have results!")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    test_google_custom_search()
