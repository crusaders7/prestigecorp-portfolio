#!/usr/bin/env python3
"""
Test script for the site audit tool functionality
"""

import requests
import json
import time
from urllib.parse import urlparse


def test_audit_api(base_url="http://localhost:3000", test_url="https://example.com"):
    """Test the audit API functionality"""

    print(f"🧪 Testing Site Audit Tool")
    print(f"API Base: {base_url}")
    print(f"Test URL: {test_url}")
    print("-" * 50)

    # Test payload
    payload = {"url": test_url}

    try:
        # Make request to audit API
        print("📡 Sending audit request...")
        start_time = time.time()

        response = requests.post(
            f"{base_url}/api/audit",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"⏱️  Response time: {duration:.2f}s")
        print(f"📊 Status code: {response.status_code}")

        if response.status_code == 200:
            results = response.json()
            print("\n✅ Audit completed successfully!")

            # Display results summary
            print("\n📋 Results Summary:")
            print(f"  Overall Score: {results.get('overall_score', 0)}/100")
            print(f"  SEO Score: {results.get('seo_score', 0)}/100")
            print(
                f"  Performance Score: {results.get('performance_score', 0)}/100")
            print(
                f"  Accessibility Score: {results.get('accessibility_score', 0)}/100")
            print(f"  Security Score: {results.get('security_score', 0)}/100")

            # Issues and recommendations
            issues = results.get('issues_found', [])
            recommendations = results.get('recommendations', [])

            print(f"\n🚨 Issues Found: {len(issues)}")
            for i, issue in enumerate(issues[:3], 1):
                print(f"  {i}. {issue}")
            if len(issues) > 3:
                print(f"  ... and {len(issues) - 3} more")

            print(f"\n💡 Recommendations: {len(recommendations)}")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec}")
            if len(recommendations) > 3:
                print(f"  ... and {len(recommendations) - 3} more")

            # Validate response structure
            print("\n🔍 Validating response structure...")
            required_fields = [
                'url', 'timestamp', 'overall_score', 'seo_score',
                'performance_score', 'accessibility_score', 'security_score'
            ]

            for field in required_fields:
                if field in results:
                    print(f"  ✅ {field}: {results[field]}")
                else:
                    print(f"  ❌ Missing field: {field}")

            # Test score validity
            scores = [
                results.get('overall_score', 0),
                results.get('seo_score', 0),
                results.get('performance_score', 0),
                results.get('accessibility_score', 0),
                results.get('security_score', 0)
            ]

            valid_scores = all(0 <= score <= 100 for score in scores)
            print(
                f"  {'✅' if valid_scores else '❌'} Score validity: {valid_scores}")

            return True

        else:
            print(f"\n❌ Audit failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text[:200]}...")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("\n🔌 Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return False


def test_multiple_urls():
    """Test multiple URLs to validate different scenarios"""
    test_urls = [
        "https://example.com",
        "https://google.com",
        "https://github.com",
        "http://httpbin.org/html",  # HTTP site for security testing
    ]

    print("\n🔄 Testing multiple URLs...")
    print("-" * 50)

    results = []
    for url in test_urls:
        print(f"\nTesting: {url}")
        success = test_audit_api("http://localhost:3000", url)
        results.append((url, success))
        time.sleep(2)  # Rate limiting

    print("\n📊 Test Results Summary:")
    print("-" * 30)
    for url, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {url}")

    success_rate = sum(1 for _, success in results if success) / len(results)
    print(f"\nSuccess Rate: {success_rate:.1%}")

    return success_rate > 0.5


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🚨 Testing error handling...")
    print("-" * 30)

    test_cases = [
        {"url": ""},  # Empty URL
        {"url": "not-a-url"},  # Invalid URL
        # Non-existent domain
        {"url": "https://this-domain-does-not-exist-12345.com"},
        {},  # Missing URL field
    ]

    for i, payload in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {payload}")
        try:
            response = requests.post(
                "http://localhost:3000/api/audit",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )

            if response.status_code >= 400:
                print(
                    f"  ✅ Correctly returned error status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(
                        f"  Error message: {error_data.get('error', 'No error message')}")
                except:
                    print(f"  Raw response: {response.text[:100]}")
            else:
                print(
                    f"  ⚠️ Unexpected success status: {response.status_code}")

        except requests.exceptions.Timeout:
            print("  ✅ Request timed out (expected for invalid domains)")
        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    print("🔧 Site Audit Tool - Comprehensive Test Suite")
    print("=" * 50)

    # Test basic functionality
    basic_test = test_audit_api()

    if basic_test:
        # Test multiple URLs
        multi_test = test_multiple_urls()

        # Test error handling
        test_error_handling()

        print("\n" + "=" * 50)
        print("🎉 Testing completed!")
        print("💡 Check the results above for any issues to address.")
    else:
        print("\n❌ Basic test failed. Please check the audit API setup.")
