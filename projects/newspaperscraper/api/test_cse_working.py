#!/usr/bin/env python3
"""Test script to verify Google CSE is working"""

from google_cse_ready import GoogleCSEManager


def test_cse():
    print("🧪 Testing Google Custom Search Engine...")

    # Create manager instance
    manager = GoogleCSEManager()

    # Test search for Shellharbour Council
    query = "shellharbour council"
    print(f"🔍 Searching for: '{query}'")

    result = manager.search(query, num=5)

    if result.get('success'):
        print("✅ Search successful!")
        print(f"📊 Total Results: {result.get('total_results', 'Unknown')}")
        print(f"📄 Items Found: {len(result.get('items', []))}")
        print("\n📝 Results:")

        for i, item in enumerate(result.get('items', [])[:5], 1):
            title = item.get('title', 'No title')
            url = item.get('link', 'No URL')
            snippet = item.get('snippet', 'No snippet')
            print(f"\n{i}. {title}")
            print(f"   🔗 {url}")
            print(f"   📋 {snippet[:100]}..." if len(
                snippet) > 100 else f"   📋 {snippet}")

        return True
    else:
        print("❌ Search failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        if 'response' in result:
            print(f"Response: {result['response']}")
        return False


if __name__ == "__main__":
    success = test_cse()
    if success:
        print("\n🎉 Google CSE is working perfectly!")
    else:
        print("\n💥 Google CSE test failed!")
