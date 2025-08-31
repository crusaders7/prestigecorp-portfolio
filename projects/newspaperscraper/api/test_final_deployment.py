#!/usr/bin/env python3
import requests
import time

print('🚀 Testing Google CSE deployment...')
print('Waiting 30 seconds for Vercel deployment...')
time.sleep(30)

try:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'shellharbour council'}, 
                           timeout=30)
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Response keys: {list(data.keys())}')
        
        if 'api_protection' in data and data['api_protection'] == 'active':
            print('✅ Google CSE with protection is working!')
            print(f'Articles found: {len(data.get("articles", []))}')
            if data.get('articles'):
                title = data["articles"][0].get("title", "No title")
                print(f'Sample: {title[:60]}')
        elif 'status' in data and data['status'] == 'fallback':
            print('⚠️  CSE fallback mode - checking why...')
            print(f'Message: {data.get("message", "No message")}')
        else:
            print('❌ Still using old format')
            print(f'Found: {data.get("found", 0)} articles')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')

# Also test the debug endpoint
print('\n🔍 Testing debug endpoint...')
try:
    response = requests.get('https://news.prestigecorp.au/api/debug', timeout=10)
    print(f'Debug Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('✅ Debug endpoint working!')
        files = data.get('files', [])
        print(f'Files in deployment: {len(files)}')
        cse_files = [f for f in files if 'protected_cse' in f or 'protection_config' in f]
        print(f'CSE-related files: {cse_files}')
    else:
        print('❌ Debug endpoint not working')
except Exception as e:
    print(f'❌ Debug failed: {e}')
