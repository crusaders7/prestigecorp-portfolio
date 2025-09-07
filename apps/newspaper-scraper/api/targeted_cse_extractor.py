#!/usr/bin/env python3
"""
Targeted Google API Key Extractor for Illawarra Mercury
Focuses specifically on the search functionality and CSE implementation

This tool:
1. Analyzes the search page specifically for Google CSE implementation
2. Intercepts and analyzes search requests
3. Looks for client-side API key usage in search functionality
4. Checks for exposed keys in search-related JavaScript
5. Attempts to reverse engineer the search implementation
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime
import base64


class GoogleCSEKeyExtractor:
    def __init__(self):
        self.base_url = "https://www.illawarramercury.com.au"
        self.search_url = "https://www.illawarramercury.com.au/search"
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.discovered_info = []

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.illawarramercury.com.au'
        })

    def extract_api_keys(self):
        """Main extraction process"""
        print("🔍 Google CSE API Key Extractor")
        print("Targeting Illawarra Mercury search functionality")
        print("=" * 55)

        # Step 1: Analyze search page implementation
        print("\n🔎 Step 1: Analyzing search page...")
        self._analyze_search_page()

        # Step 2: Perform actual search and intercept requests
        print("\n🌐 Step 2: Performing test searches...")
        self._perform_test_searches()

        # Step 3: Analyze network traffic patterns
        print("\n📡 Step 3: Analyzing network patterns...")
        self._analyze_network_patterns()

        # Step 4: Look for Google services configuration
        print("\n⚙️  Step 4: Google services analysis...")
        self._analyze_google_services()

        # Step 5: Check for iframe-based search
        print("\n🖼️  Step 5: Iframe search analysis...")
        self._analyze_iframe_search()

        # Step 6: Look for JSONP or callback patterns
        print("\n📞 Step 6: JSONP/callback analysis...")
        self._analyze_jsonp_patterns()

        # Summary
        self._print_summary()

        return self.discovered_info

    def _analyze_search_page(self):
        """Analyze the main search page for CSE implementation"""
        try:
            # Get search page
            response = self.session.get(
                f"{self.search_url}?q=test", timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for Google CSE elements
                cse_elements = soup.find_all(attrs={"data-cse-id": True})
                for element in cse_elements:
                    cse_id = element.get('data-cse-id')
                    print(f"   📍 Found CSE ID in DOM: {cse_id}")
                    self._add_discovery(
                        'cse_id_dom', cse_id, 'HTML data attribute')

                # Look for Google Custom Search script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.get('src') and 'google' in script.get('src', '').lower():
                        src = script.get('src')
                        print(f"   📜 Google script: {src}")
                        self._analyze_google_script(src)

                    # Analyze inline scripts for Google CSE
                    if script.string and 'google' in script.string.lower():
                        self._analyze_inline_google_script(script.string)

                # Look for forms with Google CSE action
                forms = soup.find_all('form')
                for form in forms:
                    action = form.get('action', '')
                    if 'google' in action.lower() or 'cse' in action.lower():
                        print(f"   📝 Google form action: {action}")
                        self._add_discovery(
                            'google_form', action, 'Form action attribute')

                # Look for hidden inputs with API keys
                inputs = soup.find_all('input', type='hidden')
                for input_elem in inputs:
                    name = input_elem.get('name', '').lower()
                    value = input_elem.get('value', '')
                    if any(keyword in name for keyword in ['key', 'api', 'token']) and 'AIza' in value:
                        print(f"   🔑 Hidden API key input: {name} = {value}")
                        self._add_discovery(
                            'hidden_input_key', value, f'Hidden input: {name}')

                print(f"   ✅ Search page analysis complete")

        except Exception as e:
            print(f"   ❌ Search page analysis error: {e}")

    def _perform_test_searches(self):
        """Perform actual searches and monitor requests"""
        test_queries = ['test', 'shellharbour', 'council', 'news']

        for query in test_queries:
            try:
                print(f"   🔍 Testing search: '{query}'")

                # Perform search
                response = self.session.get(
                    f"{self.search_url}?q={query}", timeout=10)

                if response.status_code == 200:
                    # Look for API calls in the response
                    self._extract_api_calls_from_response(response.text, query)

                    # Check response headers for clues
                    for header, value in response.headers.items():
                        if 'google' in header.lower() or 'api' in header.lower():
                            print(f"     📋 Header: {header} = {value}")
                            self._add_discovery(
                                'response_header', f"{header}: {value}", f'Search response for: {query}')

                time.sleep(2)  # Be respectful

            except Exception as e:
                print(f"     ❌ Search test error for '{query}': {e}")
                continue

    def _analyze_network_patterns(self):
        """Analyze network request patterns that might reveal API usage"""

        # Common Google API endpoints
        google_endpoints = [
            'https://www.googleapis.com/customsearch/v1',
            'https://cse.google.com/cse.js',
            'https://cse.google.com/cse/element',
            'https://www.google.com/cse/element',
            'https://programmablesearchengine.google.com'
        ]

        for endpoint in google_endpoints:
            try:
                # Try to access with our CSE ID
                test_url = f"{endpoint}?cx={self.cse_id}"
                response = self.session.get(test_url, timeout=5)

                if response.status_code == 200:
                    print(f"   📡 Accessible endpoint: {endpoint}")
                    self._extract_api_calls_from_response(
                        response.text, 'network_test')

            except Exception as e:
                continue

    def _analyze_google_services(self):
        """Look for Google services configuration that might contain API keys"""

        # Check for common Google service URLs
        google_service_paths = [
            '/gtag/js',
            '/recaptcha/api.js',
            '/maps/api/js',
            '/customsearch/v1',
            '/cse/element'
        ]

        for path in google_service_paths:
            try:
                # Look for references to these services
                main_response = self.session.get(self.base_url, timeout=10)
                if path in main_response.text:
                    print(f"   🌐 Found Google service reference: {path}")

                    # Extract the full URL
                    pattern = rf'https?://[^"\s]+{re.escape(path)}[^"\s]*'
                    matches = re.findall(pattern, main_response.text)

                    for match in matches:
                        print(f"     📍 Full URL: {match}")
                        self._extract_api_key_from_url(match)
                        self._add_discovery(
                            'google_service_url', match, 'Google service reference')

            except Exception as e:
                continue

    def _analyze_iframe_search(self):
        """Check for iframe-based Google Custom Search"""
        try:
            response = self.session.get(self.search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for iframes
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if 'google' in src.lower() or 'cse' in src.lower():
                    print(f"   🖼️  Google iframe: {src}")
                    self._extract_api_key_from_url(src)
                    self._add_discovery('google_iframe', src, 'Iframe source')

        except Exception as e:
            print(f"   ❌ Iframe analysis error: {e}")

    def _analyze_jsonp_patterns(self):
        """Look for JSONP callbacks that might expose API keys"""
        try:
            response = self.session.get(
                f"{self.search_url}?q=test", timeout=10)

            # Look for JSONP patterns
            jsonp_patterns = [
                r'callback["\'\s]*[:=]["\'\s]*([^"\';\s]+)',
                r'\.getJSON\(["\']([^"\']+)["\']',
                r'ajax\(["\']([^"\']+)["\']',
                r'fetch\(["\']([^"\']+)["\']'
            ]

            for pattern in jsonp_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if 'google' in match.lower() or 'api' in match.lower():
                        print(f"   📞 JSONP/AJAX URL: {match}")
                        self._extract_api_key_from_url(match)
                        self._add_discovery(
                            'jsonp_url', match, 'JSONP/AJAX pattern')

        except Exception as e:
            print(f"   ❌ JSONP analysis error: {e}")

    def _analyze_google_script(self, script_url):
        """Analyze external Google scripts for API keys"""
        try:
            response = self.session.get(script_url, timeout=8)
            if response.status_code == 200:
                self._extract_api_calls_from_response(
                    response.text, 'google_script')
        except Exception as e:
            pass

    def _analyze_inline_google_script(self, script_content):
        """Analyze inline scripts that mention Google"""
        self._extract_api_calls_from_response(
            script_content, 'inline_google_script')

    def _extract_api_calls_from_response(self, content, source):
        """Extract API calls and potential keys from response content"""

        # Look for Google API URLs with keys
        api_url_patterns = [
            r'https://www\.googleapis\.com/[^"\s]*[?&]key=([^"&\s]+)',
            r'https://cse\.google\.com/[^"\s]*[?&]key=([^"&\s]+)',
            r'key["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_]{39})',
            r'apikey["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_]{39})',
            r'api_key["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_]{39})'
        ]

        for pattern in api_url_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) == 39 and match.startswith('AIza'):
                    print(f"   🔑 POTENTIAL API KEY: {match}")
                    self._add_discovery('api_key', match, source)

        # Look for CSE configuration
        cse_patterns = [
            r'cx["\'\s]*[:=]["\'\s]*([^"\';\s]+)',
            r'customSearchControl["\'\s]*[:=]["\'\s]*([^"\';\s]+)',
            r'element/v1[?&]rsz=[^&]*&num=[^&]*&hl=[^&]*&source=[^&]*&gss=[^&]*&cselibv=[^&]*&cx=([^&"\']+)'
        ]

        for pattern in cse_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if ':' in match:  # CSE ID format
                    print(f"   📍 CSE configuration: {match}")
                    self._add_discovery('cse_config', match, source)

    def _extract_api_key_from_url(self, url):
        """Extract API key from URL parameters"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            for key, values in params.items():
                if key.lower() in ['key', 'apikey', 'api_key'] and values:
                    api_key = values[0]
                    if len(api_key) == 39 and api_key.startswith('AIza'):
                        print(f"   🔑 API KEY IN URL: {api_key}")
                        self._add_discovery(
                            'url_api_key', api_key, f'URL parameter: {url}')

        except Exception as e:
            pass

    def _add_discovery(self, discovery_type, value, source):
        """Add a discovery to the collection"""
        self.discovered_info.append({
            'type': discovery_type,
            'value': value,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })

    def _print_summary(self):
        """Print discovery summary"""
        print("\n" + "=" * 50)
        print("🎯 EXTRACTION SUMMARY")
        print("=" * 50)

        if not self.discovered_info:
            print("❌ No API keys or configurations discovered")
            print("\n💡 The website likely uses:")
            print("   • Server-side API calls (keys hidden)")
            print("   • Proxy endpoints for search")
            print("   • Backend services without exposing keys")
            return

        # Group by type
        by_type = {}
        for item in self.discovered_info:
            item_type = item['type']
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)

        for discovery_type, items in by_type.items():
            print(f"\n📋 {discovery_type.upper()}: {len(items)} found")
            for item in items:
                print(f"   • {item['value']}")
                print(f"     Source: {item['source']}")

        # Check for actual API keys
        api_keys = [
            item for item in self.discovered_info if item['type'] == 'api_key']
        if api_keys:
            print(f"\n🎉 FOUND {len(api_keys)} POTENTIAL API KEYS!")
            for key_info in api_keys:
                print(f"   🔑 {key_info['value']}")
                print(f"      Source: {key_info['source']}")

        # Save report
        report_file = f"cse_extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.discovered_info, f, indent=2)
        print(f"\n💾 Report saved: {report_file}")


def main():
    """Main extraction function"""
    extractor = GoogleCSEKeyExtractor()
    results = extractor.extract_api_keys()

    # Test any discovered API keys
    api_keys = [item['value'] for item in results if item['type'] == 'api_key']

    if api_keys:
        print(f"\n🧪 Testing {len(api_keys)} discovered API keys...")

        for api_key in api_keys:
            print(f"Testing: {api_key}")
            try:
                test_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=012527284968046999840:zzi3qgsoibq&q=test"
                response = requests.get(test_url, timeout=10)

                if response.status_code == 200:
                    print(f"✅ VALID API KEY: {api_key}")
                    print(f"🚀 Ready to use!")
                else:
                    print(f"❌ Invalid: HTTP {response.status_code}")
                    if response.content:
                        error_data = response.json()
                        print(
                            f"   Error: {error_data.get('error', {}).get('message', 'Unknown')}")
            except Exception as e:
                print(f"❌ Test error: {e}")
    else:
        print("\n💡 Recommendations:")
        print("   1. The website uses server-side search (good security)")
        print("   2. Get your own Google API key from Google Cloud Console")
        print("   3. Use the documented CSE ID: 012527284968046999840:zzi3qgsoibq")


if __name__ == "__main__":
    main()
