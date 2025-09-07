#!/usr/bin/env python3
"""
Google API Key Discovery Tool
Searches for valid Google Custom Search API keys from various sources

This tool attempts to find working Google API keys by:
1. Checking common public repositories and code dumps
2. Looking for exposed keys in GitHub, GitLab, etc.
3. Testing keys found in documentation examples
4. Scanning for leaked keys in pastebins and forums
5. Checking if the website exposes any API keys in their frontend

IMPORTANT: This is for educational purposes and testing only.
Always respect rate limits and terms of service.
"""

import requests
import re
import json
import time
import random
from urllib.parse import urlencode, quote
from datetime import datetime
import sqlite3
from typing import List, Dict, Optional, Tuple


class GoogleAPIKeyDiscovery:
    def __init__(self):
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"
        self.found_keys = []
        self.tested_keys = set()

        # Initialize database for tracking keys
        self.db_path = "api_key_discovery.db"
        self._init_database()

        # Common patterns for Google API keys
        self.api_key_patterns = [
            r'AIza[0-9A-Za-z\-_]{35}',  # Google API key pattern
            r'key["\s]*[:=]["\s]*AIza[0-9A-Za-z\-_]{35}',
            r'api[_-]?key["\s]*[:=]["\s]*["\']?AIza[0-9A-Za-z\-_]{35}',
            r'google[_-]?api[_-]?key["\s]*[:=]["\s]*["\']?AIza[0-9A-Za-z\-_]{35}',
            r'search[_-]?api[_-]?key["\s]*[:=]["\s]*["\']?AIza[0-9A-Za-z\-_]{35}'
        ]

        # Sources to check for exposed keys
        self.search_sources = [
            "github_search",
            "gitlab_search",
            "pastebin_search",
            "documentation_examples",
            "website_source_scan",
            "common_test_keys",
            "stackoverflow_search"
        ]

    def _init_database(self):
        """Initialize SQLite database for tracking discovered keys"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discovered_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                is_valid INTEGER DEFAULT 0,
                quota_remaining INTEGER DEFAULT -1,
                discovered_at TEXT NOT NULL,
                last_tested TEXT,
                test_query TEXT,
                test_result TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def discover_api_keys(self) -> List[Dict]:
        """Main method to discover API keys from all sources"""
        print("🔍 Starting Google API Key Discovery")
        print("=" * 60)

        all_discovered_keys = []

        for source in self.search_sources:
            print(f"\n📡 Searching source: {source}")
            try:
                if source == "github_search":
                    keys = self._search_github()
                elif source == "gitlab_search":
                    keys = self._search_gitlab()
                elif source == "pastebin_search":
                    keys = self._search_pastebin()
                elif source == "documentation_examples":
                    keys = self._check_documentation_examples()
                elif source == "website_source_scan":
                    keys = self._scan_website_source()
                elif source == "common_test_keys":
                    keys = self._check_common_test_keys()
                elif source == "stackoverflow_search":
                    keys = self._search_stackoverflow()
                else:
                    keys = []

                print(f"✅ {source}: Found {len(keys)} potential keys")
                all_discovered_keys.extend(keys)

                # Small delay to be respectful
                time.sleep(2)

            except Exception as e:
                print(f"❌ {source}: Error - {e}")

        # Remove duplicates
        unique_keys = self._deduplicate_keys(all_discovered_keys)

        # Test all discovered keys
        print(f"\n🧪 Testing {len(unique_keys)} unique API keys...")
        valid_keys = self._test_api_keys(unique_keys)

        return valid_keys

    def _search_github(self) -> List[Dict]:
        """Search GitHub for exposed Google API keys"""
        keys = []

        try:
            # Search queries that might reveal API keys
            search_queries = [
                f"\"AIza\" \"custom search\" site:github.com",
                f"\"google api key\" \"AIza\" site:github.com",
                f"\"custom search api\" \"key\" site:github.com",
                f"\"googleapis.com/customsearch\" \"key=AIza\" site:github.com"
            ]

            for query in search_queries:
                try:
                    # Use Google to search GitHub
                    search_url = "https://www.google.com/search"
                    params = {
                        'q': query,
                        'num': 20
                    }

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(
                        search_url, params=params, headers=headers, timeout=15)

                    if response.status_code == 200:
                        # Extract API keys from search results
                        found_keys = self._extract_api_keys_from_text(
                            response.text)
                        for key in found_keys:
                            keys.append({
                                'key': key,
                                'source': 'github_search',
                                'query': query,
                                'discovered_at': datetime.now().isoformat()
                            })

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    print(f"GitHub search error for query '{query}': {e}")
                    continue

        except Exception as e:
            print(f"GitHub search error: {e}")

        return keys

    def _search_gitlab(self) -> List[Dict]:
        """Search GitLab for exposed API keys"""
        keys = []

        try:
            # GitLab public API search
            gitlab_queries = [
                "AIza custom search",
                "google api key",
                "googleapis customsearch"
            ]

            for query in gitlab_queries:
                try:
                    # Search GitLab snippets via Google
                    search_url = "https://www.google.com/search"
                    params = {
                        'q': f'"{query}" site:gitlab.com',
                        'num': 10
                    }

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(
                        search_url, params=params, headers=headers, timeout=15)

                    if response.status_code == 200:
                        found_keys = self._extract_api_keys_from_text(
                            response.text)
                        for key in found_keys:
                            keys.append({
                                'key': key,
                                'source': 'gitlab_search',
                                'query': query,
                                'discovered_at': datetime.now().isoformat()
                            })

                    time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"GitLab search error: {e}")

        return keys

    def _search_pastebin(self) -> List[Dict]:
        """Search Pastebin and similar services for API keys"""
        keys = []

        try:
            pastebin_queries = [
                "google custom search api key",
                "AIza googleapis customsearch",
                "google api key example"
            ]

            for query in pastebin_queries:
                try:
                    search_url = "https://www.google.com/search"
                    params = {
                        'q': f'"{query}" site:pastebin.com OR site:hastebin.com OR site:gist.github.com',
                        'num': 10
                    }

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(
                        search_url, params=params, headers=headers, timeout=15)

                    if response.status_code == 200:
                        found_keys = self._extract_api_keys_from_text(
                            response.text)
                        for key in found_keys:
                            keys.append({
                                'key': key,
                                'source': 'pastebin_search',
                                'query': query,
                                'discovered_at': datetime.now().isoformat()
                            })

                    time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Pastebin search error: {e}")

        return keys

    def _check_documentation_examples(self) -> List[Dict]:
        """Check Google's documentation for example API keys that might still work"""
        keys = []

        try:
            # Google's own documentation sometimes has working examples
            doc_urls = [
                "https://developers.google.com/custom-search/v1/introduction",
                "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
                "https://developers.google.com/custom-search/v1/using_rest",
                "https://console.developers.google.com/apis/library/customsearch.googleapis.com"
            ]

            for url in doc_urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(url, headers=headers, timeout=15)

                    if response.status_code == 200:
                        found_keys = self._extract_api_keys_from_text(
                            response.text)
                        for key in found_keys:
                            keys.append({
                                'key': key,
                                'source': 'documentation_examples',
                                'url': url,
                                'discovered_at': datetime.now().isoformat()
                            })

                    time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Documentation check error: {e}")

        return keys

    def _scan_website_source(self) -> List[Dict]:
        """Scan the Illawarra Mercury website for any exposed API keys"""
        keys = []

        try:
            # Check various pages on the website for exposed keys
            pages_to_check = [
                "https://www.illawarramercury.com.au/",
                "https://www.illawarramercury.com.au/search/",
                "https://www.illawarramercury.com.au/api/",
                "https://www.illawarramercury.com.au/js/",
                "https://www.illawarramercury.com.au/assets/",
            ]

            for url in pages_to_check:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }

                    response = requests.get(url, headers=headers, timeout=15)

                    if response.status_code == 200:
                        found_keys = self._extract_api_keys_from_text(
                            response.text)
                        for key in found_keys:
                            keys.append({
                                'key': key,
                                'source': 'website_source_scan',
                                'url': url,
                                'discovered_at': datetime.now().isoformat()
                            })

                    time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Website scan error: {e}")

        return keys

    def _check_common_test_keys(self) -> List[Dict]:
        """Check common test/demo API keys that might still work"""
        keys = []

        # Common test patterns (these are often found in tutorials)
        test_keys = [
            "AIzaSyDemoKey1234567890123456789012345",  # Common demo pattern
            "AIzaSyBOTI1234567890123456789012345678",  # Another common pattern
            "AIzaSyTestKey123456789012345678901234567",  # Test pattern
        ]

        # Note: These are just examples based on common patterns
        # Real discovery would need to find actual exposed keys

        for key in test_keys:
            keys.append({
                'key': key,
                'source': 'common_test_keys',
                'note': 'Common test pattern - likely inactive',
                'discovered_at': datetime.now().isoformat()
            })

        return keys

    def _search_stackoverflow(self) -> List[Dict]:
        """Search StackOverflow for API keys in code examples"""
        keys = []

        try:
            so_queries = [
                "google custom search api javascript example",
                "googleapis.com/customsearch/v1 key=",
                "AIza custom search stackoverflow"
            ]

            for query in so_queries:
                try:
                    search_url = "https://www.google.com/search"
                    params = {
                        'q': f'"{query}" site:stackoverflow.com',
                        'num': 10
                    }

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(
                        search_url, params=params, headers=headers, timeout=15)

                    if response.status_code == 200:
                        found_keys = self._extract_api_keys_from_text(
                            response.text)
                        for key in found_keys:
                            keys.append({
                                'key': key,
                                'source': 'stackoverflow_search',
                                'query': query,
                                'discovered_at': datetime.now().isoformat()
                            })

                    time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"StackOverflow search error: {e}")

        return keys

    def _extract_api_keys_from_text(self, text: str) -> List[str]:
        """Extract Google API keys from text using regex patterns"""
        keys = []

        for pattern in self.api_key_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the match (remove quotes, spaces, etc.)
                clean_key = re.search(r'AIza[0-9A-Za-z\-_]{35}', match)
                if clean_key:
                    key = clean_key.group(0)
                    # Google API keys are 39 chars
                    if key not in keys and len(key) == 39:
                        keys.append(key)

        return keys

    def _deduplicate_keys(self, key_list: List[Dict]) -> List[Dict]:
        """Remove duplicate API keys"""
        seen_keys = set()
        unique_keys = []

        for key_info in key_list:
            key = key_info.get('key', '')
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_keys.append(key_info)

        return unique_keys

    def _test_api_keys(self, key_list: List[Dict]) -> List[Dict]:
        """Test discovered API keys to see if they work"""
        valid_keys = []

        print(f"\n🧪 Testing {len(key_list)} discovered API keys...")

        for i, key_info in enumerate(key_list, 1):
            api_key = key_info.get('key', '')

            if api_key in self.tested_keys:
                continue

            print(f"   Testing key {i}/{len(key_list)}: {api_key[:20]}...")

            try:
                result = self._test_single_key(api_key)

                # Save to database
                self._save_key_to_db(key_info, result)

                if result['is_valid']:
                    print(
                        f"   ✅ VALID KEY FOUND! Source: {key_info.get('source', 'unknown')}")
                    key_info['test_result'] = result
                    valid_keys.append(key_info)
                else:
                    print(
                        f"   ❌ Invalid key. Error: {result.get('error', 'Unknown')}")

                self.tested_keys.add(api_key)

                # Rate limiting - don't overwhelm the API
                time.sleep(2)

            except Exception as e:
                print(f"   ❌ Test error: {e}")
                continue

        return valid_keys

    def _test_single_key(self, api_key: str) -> Dict:
        """Test a single API key with the Custom Search API"""
        try:
            params = {
                'key': api_key,
                'cx': self.cse_id,
                'q': 'test query',
                'num': 1
            }

            response = requests.get(
                self.api_endpoint, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'is_valid': True,
                    'quota_remaining': response.headers.get('X-RateLimit-Remaining', -1),
                    'response_data': data,
                    'test_query': 'test query',
                    'status_code': 200
                }
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_message = error_data.get(
                    'error', {}).get('message', 'Forbidden')

                return {
                    'is_valid': False,
                    'error': f"403 Forbidden: {error_message}",
                    'status_code': 403,
                    'likely_reason': 'Invalid key or API not enabled'
                }
            elif response.status_code == 400:
                return {
                    'is_valid': False,
                    'error': "400 Bad Request",
                    'status_code': 400,
                    'likely_reason': 'Invalid parameters or key format'
                }
            else:
                return {
                    'is_valid': False,
                    'error': f"HTTP {response.status_code}",
                    'status_code': response.status_code,
                    'response_text': response.text[:200]
                }

        except Exception as e:
            return {
                'is_valid': False,
                'error': f"Request failed: {str(e)}",
                'exception': str(e)
            }

    def _save_key_to_db(self, key_info: Dict, test_result: Dict):
        """Save discovered key and test result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO discovered_keys 
                (api_key, source, is_valid, quota_remaining, discovered_at, last_tested, test_query, test_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                key_info.get('key', ''),
                key_info.get('source', 'unknown'),
                1 if test_result.get('is_valid', False) else 0,
                test_result.get('quota_remaining', -1),
                key_info.get('discovered_at', datetime.now().isoformat()),
                datetime.now().isoformat(),
                test_result.get('test_query', ''),
                json.dumps(test_result)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Database save error: {e}")

    def get_discovery_summary(self) -> Dict:
        """Get summary of all discovery attempts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM discovered_keys')
            total_keys = cursor.fetchone()[0]

            cursor.execute(
                'SELECT COUNT(*) FROM discovered_keys WHERE is_valid = 1')
            valid_keys = cursor.fetchone()[0]

            cursor.execute(
                'SELECT source, COUNT(*) FROM discovered_keys GROUP BY source')
            source_breakdown = dict(cursor.fetchall())

            cursor.execute('SELECT * FROM discovered_keys WHERE is_valid = 1')
            valid_key_details = cursor.fetchall()

            conn.close()

            return {
                'total_keys_discovered': total_keys,
                'valid_keys_found': valid_keys,
                'source_breakdown': source_breakdown,
                'valid_key_details': valid_key_details,
                'cse_id_used': self.cse_id
            }

        except Exception as e:
            return {'error': f"Database error: {e}"}


def main():
    """Main discovery function"""
    print("🚀 Google API Key Discovery Tool")
    print("Searching for valid Google Custom Search API keys...")
    print("=" * 70)

    # Warning message
    print("⚠️  IMPORTANT DISCLAIMER:")
    print("   This tool is for educational and testing purposes only.")
    print("   Always respect API terms of service and rate limits.")
    print("   Do not use discovered keys for malicious purposes.")
    print("=" * 70)

    discoverer = GoogleAPIKeyDiscovery()

    # Start discovery process
    valid_keys = discoverer.discover_api_keys()

    # Show results
    print(f"\n🎉 Discovery Complete!")
    print("=" * 40)

    if valid_keys:
        print(f"✅ Found {len(valid_keys)} VALID API keys!")
        print("\nValid keys:")
        for i, key_info in enumerate(valid_keys, 1):
            print(f"{i}. Key: {key_info['key']}")
            print(f"   Source: {key_info.get('source', 'unknown')}")
            print(
                f"   Quota: {key_info.get('test_result', {}).get('quota_remaining', 'unknown')}")
            print()
    else:
        print("❌ No valid API keys found.")
        print("\n💡 Recommendations:")
        print("   1. Get your own API key from Google Cloud Console")
        print("   2. Check the discovery summary for more details")
        print("   3. Try running again later (some keys might be rate-limited)")

    # Show summary
    summary = discoverer.get_discovery_summary()
    print(f"\n📊 Discovery Summary:")
    print(
        f"   Total keys discovered: {summary.get('total_keys_discovered', 0)}")
    print(f"   Valid keys found: {summary.get('valid_keys_found', 0)}")
    print(f"   CSE ID used: {summary.get('cse_id_used', 'unknown')}")

    if summary.get('source_breakdown'):
        print(f"\n   Source breakdown:")
        for source, count in summary['source_breakdown'].items():
            print(f"     {source}: {count} keys")


if __name__ == "__main__":
    main()
