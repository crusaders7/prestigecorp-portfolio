import requests
import json

# Test with minimal data
response = requests.post('https://news.prestigecorp.au/api/search', 
                        json={'query': 'test'})

print(f'Status: {response.status_code}')
result = response.json()
print(json.dumps(result, indent=2))

# Check if error field exists
if 'error' in result:
    print(f'Error: {result["error"]}')
else:
    print('No error field found')
