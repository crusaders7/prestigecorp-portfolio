import requests
import json

# Test the API again to see if it's updated
response = requests.post('https://news.prestigecorp.au/api/search', 
                        json={'query': 'test deployment check'})

print(f'Status: {response.status_code}')
result = response.json()
print('Response keys:', list(result.keys()))

# Check for specific Google CSE implementation markers
if 'cost_estimate' in result:
    print('SUCCESS: Google CSE implementation is now deployed!')
elif 'timestamp' in result:
    print('DETECTED: Implementation with timestamp field')
elif 'error' in result:
    print(f'ERROR: {result["error"]}')
else:
    print('DETECTED: Still using old implementation')

print('Sample response:')
print(json.dumps(result, indent=2))
