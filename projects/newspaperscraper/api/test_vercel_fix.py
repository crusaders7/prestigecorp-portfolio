#!/usr/bin/env python3
import requests
import time

print('🚀 Testing After Vercel Configuration Fix')
print('=' * 50)
print('Waiting 60 seconds for Vercel redeploy...')
time.sleep(60)

# Test the API after configuration fix
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
            print('🎉 SUCCESS! Google CSE is working on Vercel!')
            status = data.get('status', 'unknown')
            print(f'   Status: {status}')
            articles = data.get('articles', [])
            print(f'   Articles found: {len(articles)}')
            total = data.get('total_results', '0')
            print(f'   Total results: {total}')
            
            if articles:
                title = articles[0].get('title', 'No title')
                print(f'   Sample: {title[:80]}')
                
        elif 'total_results' in data:
            print('✅ Google CSE format detected!')
            print(f'   Total results: {data.get("total_results", "0")}')
            
        elif 'status' in data:
            status = data.get('status')
            print(f'   Status: {status}')
            if status == 'invalid_query':
                print('   ℹ️  Query too short, trying longer query...')
                
        else:
            print('❌ Still old format')
            found = data.get('found', 0)
            print(f'   Found: {found} articles (old format)')
            
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        print(f'Response: {response.text[:200]}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')

# Also test debug endpoint
print('\n🔍 Testing debug endpoint...')
try:
    response = requests.get('https://news.prestigecorp.au/api/debug', timeout=10)
    if response.status_code == 200:
        print('✅ Debug endpoint working!')
    else:
        print(f'❌ Debug status: {response.status_code}')
except Exception as e:
    print(f'❌ Debug failed: {e}')
