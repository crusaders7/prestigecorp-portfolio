#!/usr/bin/env python3
import requests
import time

print('🔍 Vercel Deployment Investigation')
print('=' * 50)

# Test 1: Check current deployment status
print('1. Testing current API response...')
try:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'test deployment'}, 
                           timeout=20)
    
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Response keys: {list(data.keys())}')
        
        # Check for new vs old format
        if 'api_protection' in data:
            print('   ✅ NEW FORMAT DETECTED!')
        elif 'total_results' in data:
            print('   ✅ GOOGLE CSE FORMAT DETECTED!')
        else:
            print('   ❌ Old format still active')
            
        # Print specific indicators
        status = data.get('status', 'No status')
        print(f'   Status field: {status}')
        
except Exception as e:
    print(f'   ❌ API test failed: {e}')

# Test 2: Check debug endpoint
print('\n2. Testing debug endpoint...')
try:
    response = requests.get('https://news.prestigecorp.au/api/debug', timeout=10)
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('   ✅ Debug endpoint working!')
        
        # Look for our files
        files = data.get('files', [])
        cse_files = [f for f in files if 'protected_cse' in f or 'search.py' in f]
        print(f'   CSE files found: {cse_files}')
        
        # Check working directory
        cwd = data.get('cwd', 'Unknown')
        print(f'   Working directory: {cwd}')
        
    elif response.status_code == 404:
        print('   ❌ Debug endpoint not deployed yet')
    else:
        print(f'   ❌ Debug error: {response.status_code}')
        
except Exception as e:
    print(f'   ❌ Debug test failed: {e}')

# Test 3: Try different endpoints
print('\n3. Testing other endpoints...')
endpoints = ['news-search', 'download', 'scrape']
for endpoint in endpoints:
    try:
        response = requests.get(f'https://news.prestigecorp.au/api/{endpoint}', timeout=5)
        print(f'   /{endpoint}: Status {response.status_code}')
    except:
        print(f'   /{endpoint}: Failed')

# Test 4: Check if it's a caching issue with headers
print('\n4. Testing with cache-busting headers...')
try:
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'If-None-Match': '*'
    }
    response = requests.post('https://news.prestigecorp.au/api/search', 
                           json={'query': 'cache-bust-test'}, 
                           headers=headers,
                           timeout=15)
    
    print(f'   Cache-bust test: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if 'api_protection' in data:
            print('   ✅ Cache busting worked!')
        else:
            print('   ❌ Still cached version')
            
except Exception as e:
    print(f'   ❌ Cache-bust failed: {e}')

print('\n🔍 Summary:')
print('   - Checking if Vercel is deploying our latest code')
print('   - Looking for signs of the new Google CSE integration')
print('   - Testing cache-busting strategies')
