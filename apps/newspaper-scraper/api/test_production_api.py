#!/usr/bin/env python3
"""
Test Production API Deployment
"""
import requests
import json
from datetime import datetime


def test_production_api():
    print('🔍 Testing Production API Deployment')
    print('=' * 50)

    try:
        # Test the production search endpoint
        response = requests.post(
            'https://news.prestigecorp.au/api/search',
            json={'query': 'shellharbour council',
                  'sources': ['illawarra_mercury']},
            timeout=30
        )

        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print(f'Response keys: {list(data.keys())}')

            # Check if it's using Google CSE (new format)
            if 'total_results' in data and 'articles' in data:
                print('✅ Using Google CSE API (new format)')
                print(f'Total results: {data.get("total_results", 0)}')
                print(f'Articles found: {len(data.get("articles", []))}')
                if data.get('articles'):
                    print(
                        f'Sample article: {data["articles"][0].get("title", "No title")[:50]}')
            else:
                print('❌ Not using Google CSE (old format)')
                print(f'Found: {data.get("found", 0)} articles')
                print(f'URLs: {len(data.get("urls", []))} URLs')

        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'Response: {response.text[:200]}')

    except requests.exceptions.RequestException as e:
        print(f'❌ Request failed: {e}')


def test_diagnostic_endpoint():
    print('\n🔍 Testing Diagnostic Endpoint')
    print('=' * 50)

    try:
        response = requests.get(
            'https://news.prestigecorp.au/api/debug', timeout=10)
        print(f'Diagnostic Status: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print('✅ Diagnostic endpoint working')
            print(f'Python version: {data.get("python_version", "Unknown")}')
            print(f'Current directory: {data.get("cwd", "Unknown")}')
            print(f'Available files: {len(data.get("files", []))} files')
        else:
            print(f'❌ Diagnostic failed: {response.status_code}')

    except Exception as e:
        print(f'❌ Diagnostic request failed: {e}')


if __name__ == '__main__':
    test_production_api()
    test_diagnostic_endpoint()
