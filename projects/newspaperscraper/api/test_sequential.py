import requests
import json

# Test the sequential strategy execution
url = "http://localhost:8000/search"
data = {
    "query": "shellharbour council",
    "sources": ["illawarra_mercury"]
}

try:
    print(f"Testing search for: {data['query']}")
    print("=" * 50)

    response = requests.post(url, json=data, timeout=120)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        articles = result.get('articles', [])
        print(f"Total articles found: {len(articles)}")

        if articles:
            print("\nFirst 5 articles:")
            for i, article in enumerate(articles[:5], 1):
                print(f"{i}. {article.get('url', 'No URL')}")
                print(f"   Title: {article.get('title', 'No Title')}")
                print()
    else:
        print(f"Error response: {response.text}")

except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to server. Make sure it's running on localhost:8000")
except Exception as e:
    print(f"ERROR: {e}")
