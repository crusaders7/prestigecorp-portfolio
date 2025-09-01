#!/usr/bin/env python3
"""
Google Custom Search API Integration Guide
Complete solution for using the discovered Google CSE configuration

DISCOVERED CONFIGURATION:
========================
Google CSE ID: 012527284968046999840:zzi3qgsoibq
Engine ID: 012527284968046999840
Search Context: zzi3qgsoibq

Additional configurations found:
- def main():
    import sys
    
    print("🔍 Google Custom Search Engine Integration")
    print("Using discovered CSE configuration from illawarramercury.com.au")
    print("=" * 70)
    
    # Create CSE manager with hardcoded API key
    cse = GoogleCSEManager()
    
    # Check if search query provided as command line argument
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print("🚀 Running Google Custom Search")
        print("=" * 60)
        
        # Search for the provided query directly
        print(f"🔍 Searching for: '{query}'")
        articles = cse.search_simple(query, max_results=10)
        
        if articles:
            print(f"✅ Found {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title']}")
                print(f"     URL: {article['url']}")
                print(f"     Snippet: {article['snippet'][:100]}...")
                print()
        else:
            print(f"❌ No articles found for '{query}'")
            # Try the full search method for more details
            full_result = cse.search(query, num=10)
            if full_result.get('success'):
                total = full_result.get('total_results', '0')
                print(f"📊 Total results available: {total}")
            else:
                print(f"🔧 Search error: {full_result.get('error', 'Unknown error')}")
    else:
        demonstration_mode()
        
        print("\n" + "="*70)
        print("💡 To search with a query, run:")
        print("   python google_cse_ready.py 'your search query'")ncSy9gevacGmVvRWjjOQdx77N528lsgT8sexk5Q9pzlDuNIjOANgEebvUgvgSeUCKM-VOPnO91qd06pFp0E=
- appKey: CYcEg3i7SYSqDiZCGHZiRA
- Google Analytics: UA-61683903-1
- Google Optimize: OPT-T2NBD8D

HOW TO GET GOOGLE API KEY:
=========================
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable the "Custom Search JSON API"
4. Go to "Credentials" and create an API Key
5. Restrict the API key to "Custom Search API" for security
6. Use the API key with our discovered CSE ID

USAGE EXAMPLE:
=============
URL Format: https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=012527284968046999840:zzi3qgsoibq&q=shellharbour
"""

import requests
import json
import re
from urllib.parse import urlencode
from datetime import datetime
from typing import List, Dict, Optional


class GoogleCSEManager:
    def __init__(self, api_key: str = None):
        # Discovered Google CSE configuration
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.engine_id = "012527284968046999840"
        self.search_context = "zzi3qgsoibq"

        # Google Custom Search API endpoint
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"

        # Set API key if provided, or use default
        # Replace with your actual API key
        self.api_key = api_key or "AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0"

        # Additional discovered configurations
        self.discovered_config = {
            "vapidPublicKey": "BMYlncSy9gevacGmVvRWjjOQdx77N528lsgT8sexk5Q9pzlDuNIjOANgEebvUgvgSeUCKM-VOPnO91qd06pFp0E=",
            "appKey": "CYcEg3i7SYSqDiZCGHZiRA",
            "google_analytics": "UA-61683903-1",
            "google_optimize_container": "OPT-T2NBD8D",
            "mailchimp_ags_account": "f821a3c0f9ebb195a03cb86d4",
            "brightcove_account": "3879528182001",
            "brightcove_player": "cdO538E0l"
        }

    def set_api_key(self, api_key: str):
        """Set the Google API key"""
        self.api_key = api_key
        print(f"✅ API key set. Ready to search using CSE ID: {self.cse_id}")

    def search(self, query: str, start: int = 1, num: int = 10) -> Dict:
        """
        Search using Google Custom Search API with discovered CSE configuration

        Args:
            query: Search query
            start: Starting index (1-based)
            num: Number of results (1-10)

        Returns:
            Dictionary with search results or error information
        """
        if not self.api_key:
            return {
                "error": "API key required",
                "setup_instructions": self.get_setup_instructions(),
                "test_url": self.get_test_url(query)
            }

        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'start': start,
                'num': num,
                'safe': 'off',  # Don't filter results
                # Only get needed fields
                'fields': 'items(title,link,snippet,displayLink,htmlTitle,htmlSnippet)',
            }

            print(f"🔍 Searching Google CSE for: '{query}'")
            response = requests.get(
                self.api_endpoint, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "query": query,
                    "total_results": data.get('searchInformation', {}).get('totalResults', '0'),
                    "search_time": data.get('searchInformation', {}).get('searchTime', '0'),
                    "items": data.get('items', []),
                    "api_response": data
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "response": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "exception": str(e)
            }

    def search_simple(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Simple search method that returns just the articles

        Returns:
            List of articles with title, url, snippet
        """
        result = self.search(query, num=min(max_results, 10))

        if result.get('success'):
            articles = []
            for item in result.get('items', []):
                articles.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'html_title': item.get('htmlTitle', ''),
                    'source': 'Google Custom Search'
                })
            return articles
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            return []

    def get_setup_instructions(self) -> Dict:
        """Get detailed setup instructions for getting a Google API key"""
        return {
            "title": "How to Get Google Custom Search API Key",
            "steps": [
                "1. Go to Google Cloud Console (https://console.cloud.google.com/)",
                "2. Create a new project or select an existing project",
                "3. Enable the 'Custom Search JSON API' in the API Library",
                "4. Go to 'Credentials' and click 'Create Credentials'",
                "5. Select 'API Key' from the dropdown",
                "6. Copy the generated API key",
                "7. (Optional) Restrict the API key to 'Custom Search API' for security",
                "8. Use the API key with this code"
            ],
            "discovered_cse_id": self.cse_id,
            "api_endpoint": self.api_endpoint,
            "cost_info": "Google Custom Search API provides 100 free queries per day, then $5 per 1000 queries",
            "documentation": "https://developers.google.com/custom-search/v1/introduction"
        }

    def get_test_url(self, query: str) -> str:
        """Get a test URL that can be used to verify the API works"""
        if not self.api_key:
            return f"{self.api_endpoint}?key=YOUR_API_KEY&cx={self.cse_id}&q={query}"
        else:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': 5
            }
            return f"{self.api_endpoint}?{urlencode(params)}"

    def test_api_key(self) -> Dict:
        """Test if the API key is working"""
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key provided",
                "instructions": self.get_setup_instructions()
            }

        # Test with a simple query that should work
        test_result = self.search("shellharbour", num=1)

        if test_result.get('success'):
            return {
                "success": True,
                "message": "API key is working correctly",
                "cse_id": self.cse_id,
                "test_query": "shellharbour",
                "results_found": len(test_result.get('items', []))
            }
        else:
            return {
                "success": False,
                "error": test_result.get('error', 'Unknown error'),
                "test_result": test_result
            }

    def get_discovered_config(self) -> Dict:
        """Get all discovered configuration from the website"""
        return {
            "google_cse": {
                "cse_id": self.cse_id,
                "engine_id": self.engine_id,
                "search_context": self.search_context,
                "api_endpoint": self.api_endpoint
            },
            "other_services": self.discovered_config,
            "source": "Extracted from illawarramercury.com.au search functionality",
            "extraction_date": "2025-08-31"
        }

    def save_config_for_reuse(self, filename: str = "google_cse_config.json"):
        """Save the discovered configuration for future use"""
        config = {
            "google_custom_search": {
                "cse_id": self.cse_id,
                "engine_id": self.engine_id,
                "search_context": self.search_context,
                "api_endpoint": self.api_endpoint,
                "api_key": "YOUR_API_KEY_HERE",  # Placeholder
                "discovered_from": "illawarramercury.com.au",
                "discovery_date": "2025-08-31"
            },
            "usage_example": {
                "python_code": '''
# Usage example:
from google_cse_manager import GoogleCSEManager

# Initialize with your API key
cse = GoogleCSEManager(api_key="YOUR_API_KEY_HERE")

# Search for articles
results = cse.search_simple("shellharbour council", max_results=10)
for article in results:
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Snippet: {article['snippet']}")
    print("-" * 50)
''',
                "curl_example": f'''
# Direct API call example:
curl "{self.api_endpoint}?key=YOUR_API_KEY&cx={self.cse_id}&q=shellharbour"
'''
            },
            "discovered_services": self.discovered_config
        }

        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration saved to {filename}")
        return filename


def demonstration_mode():
    """Demonstrate the functionality without API key"""
    print("🔧 Google Custom Search Engine Configuration")
    print("=" * 60)

    # Initialize without API key
    cse = GoogleCSEManager()

    print("📋 Discovered Configuration:")
    config = cse.get_discovered_config()
    print(f"CSE ID: {config['google_cse']['cse_id']}")
    print(f"Engine ID: {config['google_cse']['engine_id']}")
    print(f"API Endpoint: {config['google_cse']['api_endpoint']}")
    print()

    print("📝 Setup Instructions:")
    instructions = cse.get_setup_instructions()
    for step in instructions['steps']:
        print(f"  {step}")
    print()

    print("💰 Cost Information:")
    print(f"  {instructions['cost_info']}")
    print()

    print("🔗 Example URLs:")
    test_queries = ["shellharbour council",
                    "wollongong news", "illawarra events"]
    for query in test_queries:
        print(f"  {query}: {cse.get_test_url(query)}")
    print()

    print("💾 Saving configuration...")
    config_file = cse.save_config_for_reuse()
    print()

    print("🚀 Ready to use! Just add your API key:")
    print("=" * 40)
    print("# Example usage:")
    print("cse = GoogleCSEManager(api_key='YOUR_API_KEY_HERE')")
    print("results = cse.search_simple('shellharbour council')")
    print("print(f'Found {len(results)} articles')")


def api_key_mode(api_key: str):
    """Demonstrate functionality with API key"""
    print("🚀 Testing Google Custom Search with API Key")
    print("=" * 60)

    cse = GoogleCSEManager(api_key=api_key)

    # Test API key
    print("🔑 Testing API key...")
    test_result = cse.test_api_key()

    if test_result['success']:
        print(f"✅ API key is working!")
        print(
            f"   Results found for test query: {test_result['results_found']}")
        print()

        # Test some searches
        test_queries = ["shellharbour council",
                        "wollongong news", "illawarra events"]

        for query in test_queries:
            print(f"🔍 Searching for: '{query}'")
            articles = cse.search_simple(query, max_results=5)

            if articles:
                print(f"✅ Found {len(articles)} articles:")
                for i, article in enumerate(articles, 1):
                    print(f"  {i}. {article['title']}")
                    print(f"     URL: {article['url']}")
                    print(f"     Snippet: {article['snippet'][:100]}...")
                    print()
            else:
                print("❌ No articles found")

            print("-" * 50)
    else:
        print(f"❌ API key test failed: {test_result['error']}")
        print("\n📋 Setup Instructions:")
        instructions = cse.get_setup_instructions()
        for step in instructions['steps']:
            print(f"  {step}")


def main():
    """Main function - search with hardcoded API key"""
    import sys

    print("🔍 Google Custom Search Engine Integration")
    print("Using discovered CSE configuration from illawarramercury.com.au")
    print("=" * 70)

    # Create CSE manager with hardcoded API key
    cse = GoogleCSEManager()

    # Check if search query provided as command line argument
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print("🚀 Running Google Custom Search")
        print("=" * 60)

        # Search for the provided query directly
        print(f"🔍 Searching for: '{query}'")
        articles = cse.search_simple(query, max_results=10)

        if articles:
            print(f"✅ Found {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title']}")
                print(f"     URL: {article['url']}")
                print(f"     Snippet: {article['snippet'][:100]}...")
                print()
        else:
            print(f"❌ No articles found for '{query}'")
            # Try the full search method for more details
            full_result = cse.search(query, num=10)
            if full_result.get('success'):
                total = full_result.get('total_results', '0')
                print(f"📊 Total results available: {total}")
            else:
                print(
                    f"🔧 Search error: {full_result.get('error', 'Unknown error')}")
    else:
        demonstration_mode()

        print("\n" + "="*70)
        print("💡 To search with a query, run:")
        print("   python google_cse_ready.py 'your search query'")


if __name__ == "__main__":
    main()
