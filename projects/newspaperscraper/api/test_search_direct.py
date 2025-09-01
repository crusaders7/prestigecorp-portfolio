#!/usr/bin/env python3
"""
Direct test of search functionality without HTTP server
"""

import sys
import os
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testing search functionality directly...")

    # Import the handler class
    from search import handler

    # Create a mock request class for testing
    class MockRequest:
        def __init__(self, query_data):
            self.data = json.dumps(query_data).encode('utf-8')
            self.headers = {'Content-Length': len(self.data)}

        def read(self, length):
            return self.data

    # Create a mock handler with basic functionality
    class TestHandler:
        def __init__(self):
            pass

        def get_random_user_agent(self):
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'

        def search_illawarra_mercury(self, query, max_results):
            # Import the real handler's search method
            from search import handler as real_handler

            # Create a dummy handler instance for method access
            class DummyHandler:
                def get_random_user_agent(self):
                    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

            dummy = DummyHandler()

            # Get the search method from the real handler
            import types
            search_method = types.MethodType(
                real_handler.search_illawarra_mercury, dummy)

            return search_method(query, max_results)

    # Create test handler
    test_handler = TestHandler()
    print("✓ Test handler created")

    # Test the search functionality
    print("🔍 Testing search for 'shellharbour council'...")
    import time
    start_time = time.time()

    results = test_handler.search_illawarra_mercury("shellharbour council", 10)

    end_time = time.time()

    print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Found {len(results)} articles")

    for i, url in enumerate(results[:5], 1):
        print(f"{i}. {url}")

    print("✅ Search test completed successfully!")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
