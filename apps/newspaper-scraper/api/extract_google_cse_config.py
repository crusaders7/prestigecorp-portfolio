#!/usr/bin/env python3
"""
Google Custom Search Engine (CSE) Configuration Extractor
Extracts and utilizes Google CSE configuration found in website HTML/JS

Found Google CSE Configuration:
- CSE ID: 012527284968046999840:zzi3qgsoibq
- This breaks down to:
  - Engine ID: 012527284968046999840
  - Search Context: zzi3qgsoibq

Usage for Google Custom Search API:
1. The CSE ID can be used directly with Google Custom Search JSON API
2. Requires a Google API key (needs to be obtained from Google Cloud Console)
3. URL format: https://www.googleapis.com/customsearch/v1?key=[API_KEY]&cx=[CSE_ID]&q=[QUERY]
"""

import requests
import json
import re
from urllib.parse import urlencode, quote
import time


class GoogleCSEExtractor:
    def __init__(self):
        # Extracted from illawarramercury.com search results page
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.engine_id = "012527284968046999840"
        self.search_context = "zzi3qgsoibq"

        # Other extracted configs
        self.other_configs = {
            "mailchimp_ags_account_id": "f821a3c0f9ebb195a03cb86d4",
            "mailfeature_list_id": "DBEB346B-7AEE-42C9-945C-19C7D1119A4C",
            "mailchimp_the_senior_account_id": "0864364e7ccf8d854fbe6f386",
            "brightcove_account_id": "3879528182001",
            "brightcove_player_id": "cdO538E0l",
            "google_optimize_container_id": "OPT-T2NBD8D",
            "google_optimize_ga_id": "UA-61683903-1",
            "vapidPublicKey": "BMYlncSy9gevacGmVvRWjjOQdx77N528lsgT8sexk5Q9pzlDuNIjOANgEebvUgvgSeUCKM-VOPnO91qd06pFp0E",
            "appKey": "CYcEg3i7SYSqDiZCGHZiRA"
        }

    def search_without_api_key(self, query, start=1, num=10):
        """
        Attempt to use Google CSE without API key using direct site search
        This mimics how the embedded search widget works
        """
        try:
            # Method 1: Try to use the embedded CSE format
            cse_url = f"https://cse.google.com/cse/publicurl"
            params = {
                'cx': self.cse_id,
                'q': query,
                'ie': 'UTF-8',
                'start': start
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            full_url = f"{cse_url}?{urlencode(params)}"
            print(f"🔍 Searching with Google CSE: {query}")
            print(f"📡 CSE URL: {full_url}")

            response = requests.get(full_url, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_cse_results(response.text, query)
            else:
                print(
                    f"❌ CSE search failed with status: {response.status_code}")
                return self._fallback_google_search(query, start, num)

        except Exception as e:
            print(f"❌ CSE search error: {e}")
            return self._fallback_google_search(query, start, num)

    def _parse_cse_results(self, html_content, query):
        """Parse results from Google CSE HTML response"""
        results = []

        # Look for result patterns in CSE HTML
        # CSE results typically contain specific div classes
        result_patterns = [
            r'<div class="gsc-webResult.*?">.*?<a.*?href="([^"]+)".*?<div class="gsc-url-top">.*?</div>.*?</div>',
            r'<h3.*?><a.*?href="([^"]+)".*?>(.*?)</a></h3>',
            r'href="(https://www\.illawarramercury\.com\.au/[^"]+)"[^>]*>([^<]+)</a>'
        ]

        for pattern in result_patterns:
            matches = re.findall(pattern, html_content,
                                 re.DOTALL | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 1:
                    url = match[0]
                    title = match[1] if len(match) > 1 else ""

                    if 'illawarramercury.com.au' in url and url not in [r['url'] for r in results]:
                        # Clean up title
                        title = re.sub(r'<[^>]+>', '', title).strip()
                        if not title:
                            title = f"Article from Illawarra Mercury"

                        results.append({
                            'title': title,
                            'url': url,
                            'source': 'Google CSE',
                            'snippet': f"Search result for: {query}"
                        })

        # If no results found, try alternative parsing
        if not results:
            # Look for any illawarramercury.com.au links
            mercury_links = re.findall(
                r'href="(https://www\.illawarramercury\.com\.au/[^"]+)"',
                html_content,
                re.IGNORECASE
            )

            for url in mercury_links[:10]:  # Limit to first 10
                if url not in [r['url'] for r in results]:
                    results.append({
                        'title': f"Illawarra Mercury Article",
                        'url': url,
                        'source': 'Google CSE (Alternative)',
                        'snippet': f"Search result for: {query}"
                    })

        print(f"✅ Found {len(results)} results using Google CSE")
        return results

    def _fallback_google_search(self, query, start=1, num=10):
        """Fallback to regular Google search with site restriction"""
        try:
            # Use regular Google search with site: operator
            google_url = "https://www.google.com/search"
            site_query = f"site:illawarramercury.com.au {query}"

            params = {
                'q': site_query,
                'start': start - 1,  # Google uses 0-based indexing
                'num': num
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }

            full_url = f"{google_url}?{urlencode(params)}"
            print(f"🔄 Fallback to Google search: {site_query}")

            response = requests.get(full_url, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_google_results(response.text, query)
            else:
                print(f"❌ Google search also failed: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Google search error: {e}")
            return []

    def _parse_google_results(self, html_content, query):
        """Parse results from regular Google search HTML"""
        results = []

        # Google search result patterns
        patterns = [
            r'<h3[^>]*><a[^>]+href="([^"]*illawarramercury\.com\.au[^"]*)"[^>]*>([^<]+)</a></h3>',
            r'href="(https://www\.illawarramercury\.com\.au/[^"]*)"[^>]*aria-label="([^"]*)"',
            r'<a[^>]+href="([^"]*illawarramercury\.com\.au[^"]*)"[^>]*><h3[^>]*>([^<]+)</h3>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for url, title in matches:
                if url not in [r['url'] for r in results]:
                    # Clean URL (remove Google redirect)
                    if '/url?q=' in url:
                        url = re.search(r'/url\?q=([^&]+)', url)
                        if url:
                            url = url.group(1)

                    # Clean title
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if not title:
                        title = "Illawarra Mercury Article"

                    results.append({
                        'title': title,
                        'url': url,
                        'source': 'Google Search',
                        'snippet': f"Search result for: {query}"
                    })

        print(f"✅ Found {len(results)} results using Google Search fallback")
        return results

    def get_api_requirements(self):
        """Return information about getting a Google API key"""
        return {
            "google_api_key_required": True,
            "cse_id_found": self.cse_id,
            "engine_id": self.engine_id,
            "instructions": {
                "step_1": "Go to Google Cloud Console (console.cloud.google.com)",
                "step_2": "Create a new project or select existing one",
                "step_3": "Enable the Custom Search JSON API",
                "step_4": "Create credentials (API Key)",
                "step_5": "Restrict the API key to Custom Search API",
                "step_6": f"Use this CSE ID: {self.cse_id}",
                "api_url": "https://www.googleapis.com/customsearch/v1",
                "example_request": f"https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx={self.cse_id}&q=shellharbour"
            },
            "alternative_free_method": "Use the search_without_api_key() method which mimics the embedded CSE widget"
        }


def main():
    """Test the Google CSE extraction and search"""
    extractor = GoogleCSEExtractor()

    print("🔧 Google Custom Search Engine Configuration")
    print("=" * 60)
    print(f"CSE ID: {extractor.cse_id}")
    print(f"Engine ID: {extractor.engine_id}")
    print(f"Search Context: {extractor.search_context}")
    print()

    # Test search without API key
    test_queries = ["shellharbour council",
                    "wollongong news", "illawarra events"]

    for query in test_queries:
        print(f"\n🔍 Testing search for: '{query}'")
        print("-" * 40)

        results = extractor.search_without_api_key(query, num=5)

        if results:
            for i, result in enumerate(results[:5], 1):
                print(f"{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Source: {result['source']}")
                print()
        else:
            print("❌ No results found")

        # Small delay between searches
        time.sleep(2)

    print("\n📋 API Key Information")
    print("=" * 60)
    api_info = extractor.get_api_requirements()

    print(f"CSE ID Found: {api_info['cse_id_found']}")
    print(f"API Key Required: {api_info['google_api_key_required']}")
    print(f"API URL: {api_info['instructions']['api_url']}")
    print(f"Example URL: {api_info['instructions']['example_request']}")
    print()
    print("Steps to get API Key:")
    for step, instruction in api_info['instructions'].items():
        if step.startswith('step_'):
            print(f"  {step.replace('_', ' ').title()}: {instruction}")


if __name__ == "__main__":
    main()
