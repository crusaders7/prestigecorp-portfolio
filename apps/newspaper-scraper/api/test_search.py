import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin, quote_plus
import re


def test_search(query):
    """
    Tests the multi-strategy search for Illawarra Mercury.
    """
    print(f"--- Testing search for: '{query}' ---")

    # --- Strategy 1: Direct Search ---
    urls = []
    seen_urls = set()
    try:
        print("\nAttempting Direct Search...")
        direct_search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(direct_search_url, headers=headers, timeout=12)
        resp.raise_for_status()
        print(f"Direct search response: {resp.status_code}")

        soup = BeautifulSoup(resp.content, 'lxml')

        links = soup.select('.story-block__headline a')
        print(f"Found {len(links)} potential links via direct search.")

        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin("https://www.illawarramercury.com.au", href)
                if full_url not in seen_urls and 'illawarramercury.com.au/story/' in full_url:
                    seen_urls.add(full_url)
                    urls.append(full_url)

        if urls:
            print(f"Direct search SUCCEEDED with {len(urls)} results.")
            return urls

    except Exception as e:
        print(f"Direct search FAILED: {e}.")

    # --- Strategy 2: Fallback to DuckDuckGo ---
    print("\nAttempting DuckDuckGo Fallback Search...")
    try:
        ddg_search_url = "https://html.duckduckgo.com/html/"
        params = {'q': f'site:illawarramercury.com.au {query}'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        resp = requests.get(ddg_search_url, headers=headers,
                            params=params, timeout=10)
        resp.raise_for_status()
        print(f"DuckDuckGo search response: {resp.status_code}")

        # Save HTML for inspection
        with open("ddg_response.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Saved DuckDuckGo response to ddg_response.html")

        soup = BeautifulSoup(resp.text, 'lxml')

        urls = []
        seen_urls = set()

        for link in soup.find_all('a', class_='result__a'):
            href = link.get('href')
            if href:
                clean_url = unquote(href)
                match = re.search(r'uddg=([^&]+)', clean_url)
                if match:
                    actual_url = unquote(match.group(1))
                    if actual_url not in seen_urls and 'illawarramercury.com.au/story/' in actual_url:
                        seen_urls.add(actual_url)
                        urls.append(actual_url)

        if urls:
            print(f"DuckDuckGo search SUCCEEDED with {len(urls)} results.")
            return urls
        else:
            print("DuckDuckGo search found no valid results.")
            return []

    except Exception as e:
        print(f"DuckDuckGo fallback search FAILED: {e}")
        return []


if __name__ == '__main__':
    test_query = "shellharbour council"
    found_urls = test_search(test_query)
    print("\n--- FINAL RESULTS ---")
    if found_urls:
        for i, url in enumerate(found_urls):
            print(f"{i+1}: {url}")
    else:
        print("No results found from any search strategy.")
    print("----------------------")
