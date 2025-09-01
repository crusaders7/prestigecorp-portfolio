#!/usr/bin/env python3
import requests
import time

print('🔧 Testing Vercel Deployment Fixes')
print('=' * 50)
print('Waiting 60 seconds for deployment...')
time.sleep(60)

# Test 1: Simple test endpoint
print('1. Testing simple test endpoint...')
try:
    response = requests.get(
        'https://news.prestigecorp.au/api/test', timeout=15)
    print(f'   Test endpoint status: {response.status_code}')

    if response.status_code == 200:
        print('   ✅ Basic deployment is working!')
        data = response.json()
        print(
            f'   Python version: {data.get("python_version", "Unknown")[:20]}')
        imports = data.get('test_imports', {})
        for module, status in imports.items():
            if status == 'OK':
                print(f'   ✅ {module}: {status}')
            else:
                print(f'   ❌ {module}: {status}')
    else:
        print(f'   ❌ Test endpoint failed: {response.status_code}')

except Exception as e:
    print(f'   ❌ Test endpoint error: {e}')

# Test 2: Search endpoint GET method
print('\n2. Testing search endpoint GET method...')
try:
    response = requests.get(
        'https://news.prestigecorp.au/api/search', timeout=15)
    print(f'   Search GET status: {response.status_code}')

    if response.status_code == 200:
        print('   ✅ Search endpoint responding!')
        data = response.json()
        print(f'   Message: {data.get("message", "No message")}')
    else:
        print(f'   ❌ Search GET failed: {response.status_code}')

except Exception as e:
    print(f'   ❌ Search GET error: {e}')

# Test 3: Search endpoint POST method
print('\n3. Testing search endpoint POST method...')
try:
    response = requests.post('https://news.prestigecorp.au/api/search',
                             json={'query': 'test'},
                             timeout=20)
    print(f'   Search POST status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        if 'api_protection' in data:
            print('   🎉 SUCCESS! Google CSE is now working!')
        elif 'status' in data and data.get('status') != 'No status':
            print(f'   ✅ New format detected! Status: {data.get("status")}')
        else:
            print('   ⚠️  Basic response, checking format...')
            print(f'   Keys: {list(data.keys())}')
    else:
        print(f'   ❌ Search POST failed: {response.status_code}')

except Exception as e:
    print(f'   ❌ Search POST error: {e}')

print('\n📋 Summary:')
print('   - Updated Python version to 3.8 (more stable on Vercel)')
print('   - Enhanced requirements.txt with version ranges')
print('   - Added GET method for better endpoint testing')
print('   - Created simple test endpoint for diagnostics')
