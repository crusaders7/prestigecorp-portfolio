#!/usr/bin/env python3
import requests
import time

print('🚀 Testing Direct Google CSE Integration')
print('Waiting 45 seconds for Vercel deployment...')
time.sleep(45)

try:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'shellharbour council'}, 
                           timeout=30)
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Response keys: {list(data.keys())}')
        
        if 'api_protection' in data and data['api_protection'] == 'active':
            print('🎉 SUCCESS! Google CSE is working!')
            status = data.get('status', 'unknown')
            print(f'Status: {status}')
            articles = data.get('articles', [])
            print(f'Articles found: {len(articles)}')
            total = data.get('total_results', '0')
            print(f'Total results: {total}')
            if articles:
                title = articles[0].get('title', 'No title')
                print(f'First article: {title[:60]}')
        else:
            status = data.get('status', 'unknown')
            print(f'❌ Status: {status}')
            found = data.get('found', 0)
            print(f'Found: {found} articles')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        print(f'Response: {response.text[:200]}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')
