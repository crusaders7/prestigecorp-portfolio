#!/usr/bin/env python3
"""
Test script to verify that the fresh-news application is working correctly
"""

import json
import os
import sys

# Add the api directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

def test_search_api():
    """Test the search API functionality"""
    print("Testing search API...")
    
    # Import the search module
    try:
        from api.search import search_news
        print("✅ Search module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import search module: {e}")
        return False
    
    # Test the search function
    try:
        results = search_news("technology", [], 5)
        print("✅ Search function executed successfully")
        print(f"   Found {results.get('found', 0)} articles")
        return True
    except Exception as e:
        print(f"❌ Search function failed: {e}")
        return False

def test_scrape_api():
    """Test the scrape API functionality"""
    print("Testing scrape API...")
    
    # Import the scrape module
    try:
        from api.scrape import scrape_articles
        print("✅ Scrape module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import scrape module: {e}")
        return False
    
    # Test with a simple URL
    test_urls = ["https://example.com"]
    try:
        results = scrape_articles(test_urls)
        print("✅ Scrape function executed successfully")
        print(f"   Processed {results.get('total', 0)} URLs")
        return True
    except Exception as e:
        print(f"❌ Scrape function failed: {e}")
        return False

def test_download_api():
    """Test the download API functionality"""
    print("Testing download API...")
    
    # Import the download module
    try:
        from api.download import handler
        print("✅ Download module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import download module: {e}")
        return False
    
    # Test that the handler class exists
    try:
        download_handler = handler
        print("✅ Download handler class exists")
        return True
    except Exception as e:
        print(f"❌ Download handler class failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Fresh-News Application Functionality")
    print("=" * 50)
    
    # Test each API component
    tests = [
        test_search_api,
        test_scrape_api,
        test_download_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should be working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    main()