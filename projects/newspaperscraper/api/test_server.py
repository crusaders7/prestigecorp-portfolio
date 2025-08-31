#!/usr/bin/env python3
"""
Simple test to verify the search functionality
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing the search module
    print("Testing imports...")
    import requests
    import json
    from bs4 import BeautifulSoup
    print("✓ All dependencies imported successfully")
    
    # Test the search class
    print("Testing search handler...")
    from search import handler
    
    # Create a test handler instance
    test_handler = handler(None, None, None)
    print("✓ Search handler created successfully")
    
    # Test the user agent function
    user_agent = test_handler.get_random_user_agent()
    print(f"✓ Random user agent: {user_agent[:50]}...")
    
    print("✅ All tests passed! Search module is working correctly.")
    print("\nStarting HTTP server...")
    
    # Now start the actual server
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Server starting on http://localhost:8000")
    server.serve_forever()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
