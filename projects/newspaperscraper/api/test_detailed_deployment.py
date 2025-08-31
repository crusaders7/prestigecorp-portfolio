#!/usr/bin/env python3
"""
Direct test of deployed API with detailed debugging
"""

import requests
import json

def test_deployed_detailed():
    """Test with debugging information"""
    print("🔍 Comprehensive Deployment Test")
    print("=" * 50)
    
    base_url = 'https://news.prestigecorp.au'
    
    # Test different queries and see responses
    test_queries = [
        'shellharbour council',
        'wollongong hospital', 
        'illawarra'
    ]
    
    for query in test_queries:
        print(f"\n🧪 Testing query: '{query}'")
        print("-" * 40)
        
        search_data = {
            'query': query,
            'max_results': 3,
            'sources': ['illawarra_mercury']
        }
        
        try:
            response = requests.post(f'{base_url}/api/search', 
                                   json=search_data, 
                                   timeout=60)
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Print all response keys
                print(f"Response keys: {list(data.keys())}")
                
                # Check specific fields
                status = data.get('status', 'not_specified')
                found = data.get('found', 0)
                articles = data.get('articles', [])
                
                print(f"Status: {status}")
                print(f"Found: {found}")
                print(f"Articles count: {len(articles)}")
                
                # Check if we have the new fields from Google CSE
                if 'total_results' in data:
                    print(f"Total results: {data['total_results']}")
                    print("✅ Using Google CSE (has total_results field)")
                else:
                    print("❌ Not using Google CSE (missing total_results)")
                
                if 'api_protection' in data:
                    print(f"API Protection: {data['api_protection']}")
                
                # Show sample articles
                if articles:
                    print("\n📰 Sample articles:")
                    for i, article in enumerate(articles[:2], 1):
                        title = article.get('title', 'No title')
                        url = article.get('url', 'No URL')
                        print(f"  {i}. {title}")
                        print(f"     {url}")
                else:
                    print("No articles found")
                    
                # Print raw response for debugging
                print(f"\nRaw response: {json.dumps(data, indent=2)}")
                
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_deployed_detailed()
