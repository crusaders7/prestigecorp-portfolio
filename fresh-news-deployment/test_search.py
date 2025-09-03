#!/usr/bin/env python3
"""Test script for fresh-news-deployment search functionality"""

import requests
import json


def test_search_endpoint():
    """Test the search API endpoint"""
    print('=== Testing Fresh News Deployment Search Endpoint ===')

    # Test the deployed search endpoint
    try:
        print('\n1. Testing POST /api/search...')
        response = requests.post(
            'https://fresh-news-deployment-2h2wcwy61-prestigecorp4s-projects.vercel.app/api/search',
            json={'query': 'climate change', 'sources': [
                'mercury'], 'max_results': 5},
            timeout=30
        )
        print(f'Status Code: {response.status_code}')
        print(f'Response Length: {len(response.text)}')

        if response.status_code == 200:
            try:
                data = response.json()
                print(f'Found: {data.get("found", 0)} articles')
                print(f'URLs returned: {len(data.get("urls", []))}')
                if data.get("error"):
                    print(f'API Error: {data["error"]}')
                else:
                    print('✅ Search endpoint working!')
                    return True
            except json.JSONDecodeError:
                print('❌ Invalid JSON response')
                print(f'Raw response: {response.text[:200]}...')
        else:
            print(f'❌ HTTP Error {response.status_code}')
            print(f'Response: {response.text[:200]}...')

    except requests.exceptions.RequestException as e:
        print(f'❌ Request failed: {e}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')

    print('\n=== Test Complete ===')
    return False


def test_scrape_endpoint():
    """Test the scrape API endpoint"""
    print('\n=== Testing Scrape Endpoint ===')

    # Test with a sample URL
    test_urls = ['https://www.illawarramercury.com.au/story/sample-article/']

    try:
        print('\n2. Testing POST /api/scrape...')
        response = requests.post(
            'https://fresh-news-deployment-2h2wcwy61-prestigecorp4s-projects.vercel.app/api/scrape',
            json={'urls': test_urls},
            timeout=30
        )
        print(f'Status Code: {response.status_code}')
        print(f'Response Length: {len(response.text)}')

        if response.status_code == 200:
            try:
                data = response.json()
                print(f'Articles scraped: {len(data.get("articles", []))}')
                if data.get("error"):
                    print(f'API Error: {data["error"]}')
                else:
                    print('✅ Scrape endpoint responding!')
                    return True
            except json.JSONDecodeError:
                print('❌ Invalid JSON response')
                print(f'Raw response: {response.text[:200]}...')
        else:
            print(f'❌ HTTP Error {response.status_code}')
            print(f'Response: {response.text[:200]}...')

    except requests.exceptions.RequestException as e:
        print(f'❌ Request failed: {e}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')

    print('\n=== Scrape Test Complete ===')
    return False


if __name__ == '__main__':
    search_works = test_search_endpoint()
    scrape_works = test_scrape_endpoint()

    print(f'\n=== SUMMARY ===')
    print(f'Search API: {"✅ Working" if search_works else "❌ Failed"}')
    print(f'Scrape API: {"✅ Working" if scrape_works else "❌ Failed"}')
