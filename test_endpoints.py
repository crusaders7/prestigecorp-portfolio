import requests

# Test different possible endpoints
endpoints = [
    'https://news.prestigecorp.au/api/search',
    'https://news.prestigecorp.au/api/news-search',
    'https://news.prestigecorp.au/search'
]

for endpoint in endpoints:
    try:
        response = requests.post(endpoint, json={}, timeout=5)
        print(f'{endpoint}: Status {response.status_code}')
        if response.status_code == 400:
            result = response.json()
            print(f'  Error: {result.get("error", "No error field")}')
    except Exception as e:
        print(f'{endpoint}: Failed - {e}')
    print()
