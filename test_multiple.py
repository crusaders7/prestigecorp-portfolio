import requests
import json

# Test multiple queries
queries = ['test', 'council', 'news', 'local', 'illawarra']

for query in queries:
    response = requests.post('https://news.prestigecorp.au/api/search', 
                            json={'query': query, 'max_results': 2})
    
    result = response.json()
    print(f'Query: "{query}" -> Found: {result.get("found", 0)} articles')
    if result.get("found", 0) > 0:
        print(f'  First URL: {result["urls"][0][:80]}...')
    print()
