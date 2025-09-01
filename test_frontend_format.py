import requests
import json

# Test the exact request format the frontend uses
# Updated: Added error handling - trigger fresh deployment
response = requests.post('https://news.prestigecorp.au/api/search', 
                        json={
                            'query': 'council', 
                            'sources': ['illawarra_mercury'], 
                            'max_results': 10
                        },
                        headers={'Content-Type': 'application/json'})

print(f'Status: {response.status_code}')
print('Response:')

# Add error handling for JSON parsing
try:
    result = response.json()
    print(json.dumps(result, indent=2))

    if result.get('found', 0) > 0:
        print(f'\n✅ SUCCESS: Found {result["found"]} articles!')
        print('Sample articles:')
        for i, url in enumerate(result['urls'][:3], 1):
            print(f'{i}. {url}')
    else:
        print('\n❌ No articles found')
        if 'error' in result:
            print(f'Error: {result["error"]}')
except json.JSONDecodeError:
    print(f'Raw response text: {response.text}')
    print('❌ Response is not valid JSON - likely a 404 error page')
