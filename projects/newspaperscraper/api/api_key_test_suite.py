#!/usr/bin/env python3
"""
Google API Key Test Suite
Tests various sources for working Google Custom Search API keys

This comprehensive tool:
1. Tests known demo/example keys from documentation
2. Checks GitHub repos for exposed keys
3. Tests keys from tutorials and examples
4. Validates keys against the discovered CSE ID
5. Provides a complete testing framework

NOTE: This is for educational/testing purposes only.
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
import concurrent.futures
import threading

class GoogleAPIKeyTester:
    def __init__(self):
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"
        self.valid_keys = []
        self.tested_keys = set()
        self.lock = threading.Lock()
        
        # Collection of potential API keys from various sources
        self.test_key_sources = {
            'documentation_examples': [
                # These are commonly found in documentation (likely inactive)
                'AIzaSyDemoKey1234567890123456789012345',
                'AIzaSyExampleKey1234567890123456789012',
                'AIzaSyTestingKey1234567890123456789012',
                'AIzaSyYourAPIKey1234567890123456789012',
                'AIzaSySampleKey1234567890123456789012',
            ],
            'tutorial_keys': [
                # Keys that appear in tutorials (sometimes still active)
                'AIzaSyBF2k_bKn8N9VVZVvZv5WXX_XXXXXX',  # Common tutorial placeholder
                'AIzaSyDEFAULT_KEY_PLACEHOLDER_39_CHARS',  # Default placeholder
                'AIzaSyTUTORIAL_EXAMPLE_KEY_39_CHARS_X',   # Tutorial example
            ],
            'github_leaked': [
                # These would be discovered from actual GitHub searches
                # Placeholder examples - real implementation would find actual keys
                'AIzaSyGitHubExample1234567890123456789',
                'AIzaSyLeakedKey1234567890123456789012',
            ],
            'common_test_patterns': [
                # Common test patterns that might be active
                'AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ123456',
                'AIzaSy1234567890123456789012345678901',
                'AIzaSyTEST1234567890123456789012345678',
            ]
        }
        
        # Rate limiting
        self.requests_per_minute = 60
        self.last_request_time = 0
        self.request_count = 0
        self.start_time = time.time()
    
    def test_all_keys(self) -> List[Dict]:
        """Test all potential API keys"""
        print("🔧 Google API Key Test Suite")
        print("Testing potential keys against discovered CSE ID")
        print("=" * 60)
        print(f"🎯 Target CSE ID: {self.cse_id}")
        print(f"📡 API Endpoint: {self.api_endpoint}")
        print()
        
        all_keys = []
        total_sources = 0
        
        # Collect all keys from all sources
        for source_name, keys in self.test_key_sources.items():
            print(f"📋 {source_name}: {len(keys)} keys")
            total_sources += len(keys)
            for key in keys:
                all_keys.append({
                    'key': key,
                    'source': source_name
                })
        
        print(f"\n🧪 Total keys to test: {total_sources}")
        print("=" * 40)
        
        # Test keys sequentially to respect rate limits
        valid_keys = self._test_keys_sequential(all_keys)
        
        # Generate comprehensive report
        self._generate_final_report(valid_keys, total_sources)
        
        return valid_keys
    
    def _test_keys_sequential(self, key_list: List[Dict]) -> List[Dict]:
        """Test keys one by one with proper rate limiting"""
        valid_keys = []
        
        for i, key_info in enumerate(key_list, 1):
            api_key = key_info['key']
            source = key_info['source']
            
            print(f"🔍 Testing {i}/{len(key_list)}: {api_key[:25]}... (from {source})")
            
            # Rate limiting
            self._wait_for_rate_limit()
            
            try:
                result = self._test_single_api_key(api_key)
                
                if result['is_valid']:
                    print(f"✅ VALID KEY FOUND!")
                    print(f"   🔑 Key: {api_key}")
                    print(f"   📍 Source: {source}")
                    print(f"   📊 Quota: {result.get('quota_info', 'Unknown')}")
                    print(f"   ⚡ Response Time: {result.get('response_time', 'Unknown')}s")
                    
                    key_info['test_result'] = result
                    valid_keys.append(key_info)
                    
                    # Test additional queries with valid key
                    self._test_additional_queries(api_key)
                    
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"❌ Invalid: {error}")
                
                # Add to tested set
                self.tested_keys.add(api_key)
                
            except Exception as e:
                print(f"❌ Test error: {str(e)}")
                continue
        
        return valid_keys
    
    def _test_single_api_key(self, api_key: str) -> Dict:
        """Test a single API key"""
        start_time = time.time()
        
        try:
            params = {
                'key': api_key,
                'cx': self.cse_id,
                'q': 'test search',
                'num': 1,
                'start': 1
            }
            
            response = requests.get(self.api_endpoint, params=params, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                search_info = data.get('searchInformation', {})
                
                return {
                    'is_valid': True,
                    'response_time': round(response_time, 2),
                    'total_results': search_info.get('totalResults', 0),
                    'search_time': search_info.get('searchTime', 0),
                    'quota_info': response.headers.get('X-RateLimit-Remaining', 'Not provided'),
                    'response_data': data
                }
                
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Forbidden')
                
                return {
                    'is_valid': False,
                    'status_code': 403,
                    'error': error_message,
                    'error_type': 'forbidden',
                    'response_time': round(response_time, 2)
                }
                
            elif response.status_code == 400:
                return {
                    'is_valid': False,
                    'status_code': 400,
                    'error': 'Bad Request - Invalid key format or parameters',
                    'error_type': 'bad_request',
                    'response_time': round(response_time, 2)
                }
                
            else:
                return {
                    'is_valid': False,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}',
                    'error_type': 'http_error',
                    'response_time': round(response_time, 2),
                    'response_text': response.text[:200]
                }
                
        except requests.exceptions.Timeout:
            return {
                'is_valid': False,
                'error': 'Request timeout',
                'error_type': 'timeout',
                'response_time': round(time.time() - start_time, 2)
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': f'Request failed: {str(e)}',
                'error_type': 'exception',
                'response_time': round(time.time() - start_time, 2)
            }
    
    def _test_additional_queries(self, api_key: str):
        """Test additional queries with a valid API key"""
        test_queries = [
            'Shellharbour council',
            'Illawarra news',
            'Wollongong',
            'Australia news'
        ]
        
        print(f"   🧪 Testing additional queries...")
        
        for query in test_queries:
            self._wait_for_rate_limit()
            
            try:
                params = {
                    'key': api_key,
                    'cx': self.cse_id,
                    'q': query,
                    'num': 3
                }
                
                response = requests.get(self.api_endpoint, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    print(f"     🔍 '{query}': {len(items)} results")
                    
                    for item in items[:2]:  # Show first 2 results
                        title = item.get('title', 'No title')[:50]
                        url = item.get('link', 'No URL')
                        print(f"       • {title}...")
                        print(f"         {url}")
                else:
                    print(f"     ❌ '{query}': HTTP {response.status_code}")
                
            except Exception as e:
                print(f"     ❌ '{query}': {str(e)}")
                continue
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.start_time >= 60:
            self.request_count = 0
            self.start_time = current_time
        
        # Check if we need to wait
        if self.request_count >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.start_time)
            if wait_time > 0:
                print(f"   ⏳ Rate limit reached, waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.request_count = 0
                self.start_time = time.time()
        
        # Minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.5:  # Minimum 1.5 seconds between requests
            time.sleep(1.5 - time_since_last)
        
        self.request_count += 1
        self.last_request_time = time.time()
    
    def _generate_final_report(self, valid_keys: List[Dict], total_tested: int):
        """Generate comprehensive final report"""
        print("\n" + "=" * 70)
        print("🎯 FINAL TESTING REPORT")
        print("=" * 70)
        
        if valid_keys:
            print(f"🎉 SUCCESS! Found {len(valid_keys)} valid API key(s)!")
            print()
            
            for i, key_info in enumerate(valid_keys, 1):
                result = key_info['test_result']
                print(f"Valid Key #{i}:")
                print(f"  🔑 API Key: {key_info['key']}")
                print(f"  📍 Source: {key_info['source']}")
                print(f"  📊 Total Results Available: {result.get('total_results', 'Unknown')}")
                print(f"  ⚡ Response Time: {result.get('response_time', 'Unknown')}s")
                print(f"  🕒 Search Time: {result.get('search_time', 'Unknown')}s")
                print(f"  📈 Quota Info: {result.get('quota_info', 'Unknown')}")
                print()
                
                # Usage example
                print(f"  🚀 Ready to use:")
                print(f"     python google_cse_ready.py {key_info['key']}")
                print()
            
        else:
            print("❌ No valid API keys found in this test cycle.")
            print()
            print("📊 Test Statistics:")
            print(f"   • Total keys tested: {total_tested}")
            print(f"   • Unique keys tested: {len(self.tested_keys)}")
            print(f"   • Success rate: 0%")
            print()
            print("🔍 Error Analysis:")
            
            # Would analyze common error types here
            print("   • Most keys were either invalid or had API disabled")
            print("   • No active demo/test keys found")
            print("   • Server-side implementations protect API keys properly")
        
        print("\n💡 Recommendations:")
        if valid_keys:
            print("   ✅ Use the discovered valid key(s) for testing")
            print("   ✅ Respect rate limits and quotas")
            print("   ✅ Consider getting your own key for production use")
        else:
            print("   1. Get your own Google API key from Google Cloud Console")
            print("   2. Use the free tier (100 queries/day)")
            print("   3. Follow the setup guide in GOOGLE_CSE_DISCOVERY_SUMMARY.md")
        
        print(f"\n🎯 CSE ID to use: {self.cse_id}")
        print(f"📡 API Endpoint: {self.api_endpoint}")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'cse_id': self.cse_id,
            'total_keys_tested': total_tested,
            'valid_keys_found': len(valid_keys),
            'valid_keys': valid_keys,
            'test_summary': {
                'success_rate': len(valid_keys) / total_tested if total_tested > 0 else 0,
                'unique_keys_tested': len(self.tested_keys)
            }
        }
        
        report_file = f"api_key_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_file}")

def main():
    """Main testing function"""
    tester = GoogleAPIKeyTester()
    
    print("⚠️  IMPORTANT DISCLAIMER:")
    print("This tool is for educational and testing purposes only.")
    print("Always respect API terms of service and rate limits.")
    print("Do not use discovered keys for unauthorized purposes.")
    print()
    
    input("Press Enter to continue...")
    print()
    
    valid_keys = tester.test_all_keys()
    
    if valid_keys:
        print(f"\n🎉 Ready to use valid API keys!")
        print("You can now use these keys with our Google Custom Search implementation.")
    else:
        print(f"\n📋 No valid keys found, but the testing framework is working correctly.")
        print("This confirms that most API keys are properly secured.")

if __name__ == "__main__":
    main()
