#!/usr/bin/env python3
import requests
import time

print('🧪 Testing Minimal Endpoint')
print('Waiting 45 seconds for deployment...')
time.sleep(45)

try:
    response = requests.get(
        'https://news.prestigecorp.au/api/minimal', timeout=10)
    print(f'Minimal endpoint: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        message = data.get('message', 'Working')
        print(f'✅ SUCCESS: {message}')
        version = data.get('version', 'Unknown')
        print(f'Version: {version}')
        print('🎉 Deployment infrastructure is working!')
    else:
        print(f'❌ Failed: {response.status_code}')
        print('Deployment may still be building...')
except Exception as e:
    print(f'❌ Error: {e}')
    print('Network or deployment issue')
