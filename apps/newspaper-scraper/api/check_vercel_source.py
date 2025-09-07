#!/usr/bin/env python3
"""
Check what code Vercel is actually running by testing specific endpoints
"""
import requests


def check_vercel_deployment():
    print('🕵️ Vercel Deployment Source Investigation')
    print('=' * 60)

    # Test what endpoints exist
    base_url = 'https://news.prestigecorp.au/api'
    endpoints_to_test = [
        'search',      # Should exist (we see it working)
        'minimal',     # Our new test endpoint
        'test',        # Our diagnostic endpoint
        'debug',       # Our debug endpoint
        'protected_cse'  # Our CSE file
    ]

    print('🔍 Testing endpoint availability:')
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f'{base_url}/{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f'   ✅ /{endpoint}: Working (200)')
            elif response.status_code == 404:
                print(f'   ❌ /{endpoint}: Not found (404)')
            elif response.status_code == 501:
                print(
                    f'   ⚠️  /{endpoint}: Exists but method not supported (501)')
            else:
                print(f'   ❓ /{endpoint}: Status {response.status_code}')
        except:
            print(f'   ❌ /{endpoint}: Failed to connect')

    print('\n🔍 Testing search endpoint behavior:')
    try:
        # Test POST to search
        response = requests.post(f'{base_url}/search',
                                 json={'query': 'version-test'},
                                 timeout=10)

        if response.status_code == 200:
            data = response.json()
            keys = list(data.keys())
            print(f'   Response keys: {keys}')

            # Check for indicators of which version
            if 'api_protection' in data:
                print('   🎉 NEW VERSION: Google CSE detected!')
            elif 'total_results' in data:
                print('   ✅ NEWER VERSION: CSE format detected!')
            elif 'query' in data and 'found' in data and 'urls' in data:
                print('   ❌ OLD VERSION: Web scraping format detected!')
            else:
                print(f'   ❓ UNKNOWN VERSION: Keys {keys}')
        else:
            print(f'   ❌ Search test failed: {response.status_code}')

    except Exception as e:
        print(f'   ❌ Search test error: {e}')

    print('\n💡 DIAGNOSIS:')
    print('If minimal/test/debug endpoints show 404:')
    print('→ Vercel is deploying from wrong commit/branch')
    print('If search shows old format:')
    print('→ Vercel is using cached or different source code')


if __name__ == '__main__':
    check_vercel_deployment()
