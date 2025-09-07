import requests
import json

print('🧪 TESTING VERCEL DEPLOYMENT...')
print('='*40)

# Test with empty request to check error message
response = requests.post('https://news.prestigecorp.au/api/search', json={})
print(f'Status: {response.status_code}')

try:
    result = response.json()
    error_msg = result.get('error', 'No error field')
    print(f'Error message: "{error_msg}"')
    
    if 'UPDATED_API_v2' in error_msg:
        print('🎉 SUCCESS! The correct Google CSE code is now deployed!')
        print('✅ Root directory fix worked!')
    elif 'Please enter a search term' in error_msg:
        print('❌ Still using old code - deployment may need more time')
        print('⏳ Vercel might be caching or still deploying...')
    else:
        print(f'🤔 Unexpected error message: {error_msg}')
        
except Exception as e:
    print(f'❌ Error parsing response: {e}')
    print(f'Raw response: {response.text[:200]}')

print('\n' + '='*40)
