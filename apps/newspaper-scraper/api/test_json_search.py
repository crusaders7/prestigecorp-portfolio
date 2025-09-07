#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
import json


def test_json_search():
    """Test the JSON search endpoint"""
    print("Testing JSON search endpoint...")

    query = "shellharbour council"
    search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}&format=json"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.illawarramercury.com.au/'
    }

    try:
        resp = requests.get(search_url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            content = resp.text
            print(f"Response length: {len(content)} characters")

            # Save the full response to examine
            with open('search_json_response.json', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Saved response to search_json_response.json")

            # Try to parse as JSON
            try:
                data = json.loads(content)
                print(f"Successfully parsed JSON!")
                print(f"Top-level keys: {list(data.keys())}")

                # Look for results
                if 'results' in data:
                    results = data['results']
                    print(f"Found {len(results)} results")

                    for i, result in enumerate(results[:5], 1):
                        print(f"\n{i}. Result keys: {list(result.keys())}")
                        if 'title' in result:
                            print(f"   Title: {result['title']}")
                        if 'url' in result:
                            print(f"   URL: {result['url']}")
                        if 'snippet' in result:
                            print(f"   Snippet: {result['snippet'][:100]}...")

                # Check other possible structures
                for key in data.keys():
                    if isinstance(data[key], list) and len(data[key]) > 0:
                        print(f"\nKey '{key}' contains {len(data[key])} items")
                        if isinstance(data[key][0], dict):
                            print(
                                f"  First item keys: {list(data[key][0].keys())}")

            except json.JSONDecodeError as e:
                print(f"Failed to parse as JSON: {e}")
                print(f"First 500 chars: {content[:500]}")

                # Look for story URLs in raw text
                import re
                story_urls = re.findall(
                    r'https://www\.illawarramercury\.com\.au/story/[^"\'>\s]+', content)
                if story_urls:
                    print(f"\nFound {len(story_urls)} story URLs in raw text:")
                    for i, url in enumerate(story_urls[:10], 1):
                        print(f"{i}. {url}")
        else:
            print(f"Failed: {resp.status_code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_json_search()
