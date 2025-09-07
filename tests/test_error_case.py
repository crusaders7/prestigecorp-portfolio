import requests
import json

# Test with empty query to trigger error handling
response = requests.post('https://news.prestigecorp.au/api/search', 
                        json={'query': ''})

print(f'Status: {response.status_code}')
result = response.json()
print('Response keys:', list(result.keys()))

if 'error' in result:
    print(f'Error message: {result["error"]}')
    print('This indicates the new implementation is working!')
elif 'found' in result:
    print('Still getting search results format')

print('Full response:')
print(json.dumps(result, indent=2))
