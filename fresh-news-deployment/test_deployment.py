#!/usr/bin/env python3
"""
Fresh News Deployment Diagnostic Tool
Tests all aspects of the news search functionality
"""

import requests
import json
import time
from datetime import datetime


def test_fresh_news_deployment():
    """Comprehensive test of fresh-news-deployment"""

    print("🔍 Fresh News Deployment - Comprehensive Diagnostic")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Test different possible deployment URLs
    test_urls = [
        "https://prestigecorp.au/api/search",  # Custom domain
        "https://news.prestigecorp.au/api/search",  # Custom subdomain
        "http://localhost:3000/api/search",  # Local testing
        "https://prestigecorp-portfolio.vercel.app/api/search",  # Vercel default
    ]

    for i, base_url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {base_url}")
        print("-" * 40)

        try:
            # Test with a simple search request
            test_payload = {
                "query": "test news",
                "sources": ["mercury"],
                "max_results": 3
            }

            print("📡 Sending test request...")
            start_time = time.time()

            response = requests.post(
                base_url,
                headers={"Content-Type": "application/json"},
                json=test_payload,
                timeout=15
            )

            end_time = time.time()
            duration = end_time - start_time

            print(f"⏱️  Response time: {duration:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ SUCCESS! API is responding")
                    print(f"   Found: {data.get('found', 0)} articles")
                    print(f"   Query: {data.get('query', 'N/A')}")
                    print(f"   Sources: {data.get('sources_searched', [])}")

                    if data.get('error'):
                        print(f"⚠️  API Error: {data['error']}")

                    return True, base_url

                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"   Raw response: {response.text[:200]}...")

            elif response.status_code == 404:
                print("❌ Endpoint not found (404)")
                print("   This URL doesn't have the search API deployed")

            elif response.status_code == 500:
                print("❌ Server error (500)")
                try:
                    error_data = response.json()
                    print(
                        f"   Error: {error_data.get('error', 'Unknown server error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}...")

            elif response.status_code == 502:
                print("❌ Bad Gateway (502)")
                print("   Vercel function may have crashed or timed out")

            elif response.status_code == 401 or response.status_code == 403:
                print("❌ Authentication/Permission error")
                print("   API credentials may be invalid or missing")

            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except requests.exceptions.Timeout:
            print("⏰ Request timed out (15s)")
            print("   Server may be slow or unresponsive")

        except requests.exceptions.ConnectionError:
            print("🔌 Connection error")
            print("   URL may not exist or network issues")

        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")

    print("\n" + "=" * 60)
    print("🔧 DIAGNOSIS COMPLETE")
    print("=" * 60)
    print("❌ All endpoints failed. Possible issues:")
    print("   1. Deployment not completed or failed")
    print("   2. API endpoints not deployed to Vercel")
    print("   3. Google API credentials not configured")
    print("   4. CORS or network configuration issues")
    print("   5. Vercel function errors or timeouts")
    print("\n💡 Recommended fixes:")
    print("   1. Deploy fresh-news-deployment to Vercel")
    print("   2. Configure Google API key and CSE ID in Vercel dashboard")
    print("   3. Check Vercel function logs for errors")
    print("   4. Verify vercel.json routing configuration")

    return False, None


def test_frontend_connectivity():
    """Test if the frontend can reach any API"""
    print("\n🌐 Testing Frontend Connectivity")
    print("-" * 40)

    # Test frontend pages
    frontend_urls = [
        "https://prestigecorp.au",
        "https://news.prestigecorp.au",
        "https://prestigecorp-portfolio.vercel.app"
    ]

    for url in frontend_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - Frontend accessible")
                if "fresh-news-deployment" in response.text or "News Scraper" in response.text:
                    print("   Contains news scraper interface")
            else:
                print(f"❌ {url} - Status {response.status_code}")

        except Exception as e:
            print(f"❌ {url} - Error: {str(e)}")


if __name__ == "__main__":
    # Run comprehensive diagnostic
    success, working_url = test_fresh_news_deployment()
    test_frontend_connectivity()

    if success:
        print(f"\n🎉 Working API found at: {working_url}")
        print("The search functionality should work from the frontend!")
    else:
        print("\n❌ No working API endpoints found.")
        print("The search feature will not work until deployment issues are resolved.")

    print(f"\n📊 Diagnostic completed at {datetime.now().strftime('%H:%M:%S')}")
