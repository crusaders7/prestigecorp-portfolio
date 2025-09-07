#!/usr/bin/env python3

from urllib.parse import urljoin
import json
from bs4 import BeautifulSoup
import requests
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the handler and test directly


def test_current_search():
    """Test current search implementation directly"""

    # Simulate the POST request that the frontend would make
    payload = {
        'query': 'shellharbour council',
        'sources': ['illawarra_mercury'],
        'max_results': 20
    }

    print("Testing current search implementation...")
    print(f"Query: {payload['query']}")

    # Import and use the search logic directly
    from search import handler

    class MockRequest:
        def __init__(self, data):
            self.data = data

        def read(self, length=None):
            return json.dumps(self.data).encode()

    class MockHeaders:
        def get(self, key, default=None):
            if key == 'Content-Length':
                return len(json.dumps(payload))
            return default

    # Create a mock handler instance
    test_handler = handler()
    test_handler.headers = MockHeaders()
    test_handler.rfile = MockRequest(payload)

    # Call the search method directly
    try:
        results = test_handler.search_illawarra_mercury(
            'shellharbour council', 20)

        print(f"\nFound {len(results)} articles:")
        for i, article in enumerate(results, 1):
            print(f"{i}. {article.get('title', 'No title')}")
            print(f"   URL: {article.get('url', 'No URL')}")
            if article.get('date'):
                print(f"   Date: {article.get('date')}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_current_search()
