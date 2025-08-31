#!/usr/bin/env python3
import requests
import time

print('🚀 Testing Cache-Busting Deployment')
print('=' * 50)
print('Waiting 45 seconds for Vercel deployment...')
time.sleep(45)

# Test the rewritten endpoint
try:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'shellharbour council'}, 
                           timeout=30)
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Response keys: {list(data.keys())}')
        
        # Check for Google CSE indicators
        if 'api_protection' in data and data['api_protection'] == 'active':
            print('🎉 BREAKTHROUGH! Google CSE is working!')
            print(f'   Status: {data.get("status", "unknown")}')
            print(f'   Articles: {len(data.get("articles", []))}')
            print(f'   Total results: {data.get("total_results", "0")}')
            
        elif 'total_results' in data:
            print('✅ Google CSE format detected!')
            
        else:
            print('❌ Still old format')
            print(f'   Keys found: {list(data.keys())}')
            
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')

# Also test direct access to the new endpoint
print('\n🔍 Testing direct search-new endpoint...')
try:
    response = requests.post('https://news.prestigecorp.au/api/search-new', 
                           json={'query': 'shellharbour council'}, 
                           timeout=20)
    
    print(f'Direct endpoint status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if 'api_protection' in data:
            print('✅ Direct endpoint has Google CSE!')
        else:
            print('❌ Direct endpoint still old format')
            
except Exception as e:
    print(f'❌ Direct test failed: {e}')
