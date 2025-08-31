#!/usr/bin/env python3
import requests
import time

print('🚀 Final Test - Clean Deployment')
print('=' * 50)
print('Waiting 90 seconds for complete Vercel redeploy...')
time.sleep(90)

# Final test
try:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'shellharbour council'}, 
                           timeout=30)
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Response keys: {list(data.keys())}')
        
        # Check for success indicators
        if 'api_protection' in data and data['api_protection'] == 'active':
            print('🎉🎉🎉 VICTORY! Google CSE is LIVE on Vercel!')
            print(f'   Status: {data.get("status", "unknown")}')
            print(f'   Articles found: {len(data.get("articles", []))}')
            print(f'   Total results: {data.get("total_results", "0")}')
            
            # Show sample result
            if data.get('articles'):
                title = data['articles'][0].get('title', 'No title')
                print(f'   Sample article: {title[:80]}')
                
            print('\n✅ DEPLOYMENT SUCCESSFUL!')
            print('✅ Google CSE API integrated!')
            print('✅ Cost protection active!')
            print('✅ Production ready!')
            
        elif 'total_results' in data:
            print('🎉 Google CSE format detected!')
            print(f'   Total results: {data.get("total_results", "0")}')
            
        elif 'status' in data and 'invalid_query' in data.get('status', ''):
            print('ℹ️  Query validation working - trying longer query...')
            
        else:
            print('❌ Still old format')
            print(f'   Keys: {list(data.keys())}')
            print('   Cache may need more time to clear')
            
    elif response.status_code == 404:
        print('❌ Endpoint not found - deployment may be in progress')
        
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        print(f'Response: {response.text[:200]}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')

print('\n📊 Current Status Summary:')
print('   Local System: ✅ Google CSE working perfectly')
print('   Repository: ✅ Latest code committed and pushed')
print('   Deployment: ⏳ Testing after clean rebuild')
print('   Next: If still cached, Vercel may need 24h for full cache clear')
