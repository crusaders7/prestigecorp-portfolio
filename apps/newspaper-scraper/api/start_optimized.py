#!/usr/bin/env python3
"""
Start the optimized search server with proper error handling
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🚀 Starting optimized search server...")
    from search_optimized import handler
    from http.server import HTTPServer

    # Use port 8001 to avoid conflicts
    server = HTTPServer(('localhost', 8001), handler)
    print("🌟 Optimized Search API starting on http://localhost:8001")
    print("📊 Based on performance testing - Strategy 2 (Category Scraping) prioritized")
    server.serve_forever()

except KeyboardInterrupt:
    print("\n🛑 Server stopped by user.")
    server.shutdown()
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
