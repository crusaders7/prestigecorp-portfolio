#!/usr/bin/env python3
"""
Test the deployed Google CSE API protection system on Vercel
"""

import requests
import json


def test_deployed_api():
    """Test the deployed search API"""
    base_url = 'https://news.prestigecorp.au'

    print("🧪 Testing Deployed API Protection System")
    print("=" * 50)
    print(f"Target: {base_url}")
    print()

    # Test the search endpoint
    search_data = {
        'query': 'shellharbour council',
        'sources': ['illawarra_mercury'],
        'max_results': 5
    }

    try:
        print("🔍 Testing search API...")
        response = requests.post(f'{base_url}/api/search',
                                 json=search_data,
                                 timeout=60)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"✅ API is working!")
            print(f"Articles found: {len(articles)}")

            if articles:
                print("\n📰 Sample Results:")
                for i, article in enumerate(articles[:3], 1):
                    title = article.get('title', 'No title')
                    url = article.get('url', 'No URL')
                    print(f"  {i}. {title}")
                    print(f"     {url}")
                    print()
            else:
                print("⚠️  No articles returned")
                print("Response data:", data)

        else:
            print(f"❌ API Error: {response.status_code}")
            print("Response:", response.text[:300])

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_protection_endpoints():
    """Test if protection files are accessible"""
    base_url = 'https://news.prestigecorp.au'

    print("\n🛡️ Testing Protection Endpoints")
    print("=" * 50)

    # These might not be directly accessible in Vercel deployment
    protection_files = [
        '/protected_cse.py',
        '/usage_monitor.py',
        '/api/protected_cse.py',
        '/api/usage_monitor.py'
    ]

    for endpoint in protection_files:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: Accessible")
            elif response.status_code == 404:
                print(f"❌ {endpoint}: Not found (expected in Vercel)")
            else:
                print(f"⚠️  {endpoint}: Status {response.status_code}")
        except:
            print(f"❌ {endpoint}: Connection failed")


def test_google_cse_direct():
    """Test if we can use Google CSE directly from local environment"""
    print("\n🔧 Testing Local Google CSE Access")
    print("=" * 50)

    try:
        # Test our local protected CSE
        from protected_cse import ProtectedGoogleCSE

        cse = ProtectedGoogleCSE()
        print("✅ Local CSE initialized")

        # Test a search
        articles = cse.search_simple("shellharbour council", max_results=3)

        if articles:
            print(f"✅ Local CSE working: {len(articles)} articles found")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title'][:50]}...")
        else:
            print("❌ Local CSE returned no results")

    except Exception as e:
        print(f"❌ Local CSE error: {e}")


if __name__ == "__main__":
    test_deployed_api()
    test_protection_endpoints()
    test_google_cse_direct()
