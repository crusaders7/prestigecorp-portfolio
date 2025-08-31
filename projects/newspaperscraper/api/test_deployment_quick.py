#!/usr/bin/env python3
import requests
import time

print('Testing deployment after push...')
time.sleep(10)

# Test debug endpoint
try:
    response = requests.get('https://news.prestigecorp.au/api/debug', timeout=10)
    print(f'Debug status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('✅ Debug working!')
        print(f'Files: {len(data.get("files", []))}')
    else:
        print('❌ Debug not working')
except Exception as e:
    print(f'Debug error: {e}')

# Test search endpoint  
try:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'test'}, timeout=10)
    print(f'Search status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Search keys: {list(data.keys())}')
        if 'total_results' in data:
            print('✅ Google CSE deployed!')
        else:
            print('❌ Still old format')
except Exception as e:
    print(f'Search error: {e}')
