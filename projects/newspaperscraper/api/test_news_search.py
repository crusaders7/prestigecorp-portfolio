#!/usr/bin/env python3
import requests

print('Testing news-search endpoint...')
response = requests.post('https://news.prestigecorp.au/api/news-search',
                         json={'query': 'shellharbour council'},
                         timeout=30)

print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Keys: {list(data.keys())}')
    if 'total_results' in data:
        print('✅ Google CSE working!')
        print(f'Found: {len(data.get("articles", []))} articles')
    else:
        print('❌ Old format')
else:
    print(f'Error: {response.text[:100]}')
