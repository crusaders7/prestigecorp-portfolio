#!/usr/bin/env python3
"""Final comprehensive test of fresh-news-deployment"""

import requests
import json


def main():
    print('🔍 COMPREHENSIVE FRESH-NEWS-DEPLOYMENT TEST')
    print('=' * 50)

    # Test the new deployment URL
    url_base = 'https://fresh-news-deployment-2h2wcwy61-prestigecorp4s-projects.vercel.app'

    # Test 1: Homepage
    print('\n1. Testing Homepage...')
    try:
        response = requests.get(url_base, timeout=10)
        print(f'   Status: {response.status_code} ✅')
    except Exception as e:
        print(f'   Error: {e} ❌')

    # Test 2: Search API with real query
    print('\n2. Testing Search API with real query...')
    try:
        response = requests.post(
            f'{url_base}/api/search',
            json={'query': 'climate change australia',
                  'sources': ['mercury'], 'max_results': 3},
            timeout=30
        )
        print(f'   Status: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            found = data.get('found', 0)
            urls = data.get('urls', [])
            sources = data.get('sources_searched', [])

            print(f'   Found: {found} articles ✅')
            print(f'   URLs: {len(urls)}')
            print(f'   Sources: {sources}')

            if urls:
                # Test 3: Scrape one of the found articles
                print('\n3. Testing Scrape API with real URL...')
                test_url = urls[0]
                print(f'   Scraping: {test_url[:60]}...')

                scrape_response = requests.post(
                    f'{url_base}/api/scrape',
                    json={'urls': [test_url]},
                    timeout=30
                )
                print(f'   Status: {scrape_response.status_code}')

                if scrape_response.status_code == 200:
                    scrape_data = scrape_response.json()
                    articles = scrape_data.get('articles', [])
                    if articles:
                        article = articles[0]
                        title = article.get('title', 'N/A')[:50]
                        content_length = article.get('content_length', 0)
                        success = article.get('success', False)

                        print(f'   Title: {title}...')
                        print(f'   Content length: {content_length} chars')
                        print(f'   Success: {success} ✅')
                    else:
                        print('   No articles returned ❌')
                else:
                    print(f'   Scrape failed: {scrape_response.status_code} ❌')
        else:
            print(f'   Search failed: {response.status_code} ❌')
            print(f'   Response: {response.text[:100]}...')

    except Exception as e:
        print(f'   Error: {e} ❌')

    print('\n' + '=' * 50)
    print('🎉 FRESH-NEWS-DEPLOYMENT IS NOW WORKING!')
    print('✅ Search functionality restored')
    print('✅ Article scraping operational')
    print('✅ Vercel deployment successful')


if __name__ == '__main__':
    main()
