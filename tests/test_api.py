import requests
import json

# Test the API
response = requests.post('https://news.prestigecorp.au/api/search', 
                        json={'query': 'council', 'sources': ['illawarra_mercury'], 'max_results': 3})

print(f'Status: {response.status_code}')
print('Response:')
try:
    result = response.json()
    print(json.dumps(result, indent=2))
    if 'found' in result:
        print(f'Articles found: {result["found"]}')
except:
    print(response.text)
