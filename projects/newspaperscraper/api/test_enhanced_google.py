#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus, unquote
import time
import re

def test_enhanced_google_search():
    """Test the enhanced Google site search approach"""
    print("Testing enhanced Google site search for 'shellharbour council'...")
    
    query = "shellharbour council"
    max_results = 15
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    urls = []
    seen_urls = set()
    
    # Try both quoted and unquoted searches
    search_queries = [
        f'site:illawarramercury.com.au "{query}"',  # Exact phrase first
        f'site:illawarramercury.com.au {query}',    # Individual words
    ]
    
    for search_query in search_queries:
        print(f"\nTrying Google search: {search_query}")
        google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&num=20"
        print(f"URL: {google_url}")
        
        try:
            resp = requests.get(google_url, headers=headers, timeout=12)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'lxml')

                found_in_this_search = 0
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if '/url?q=' in href:
                        # Extract actual URL from Google redirect
                        match = re.search(r'/url\?q=([^&]+)', href)
                        if match:
                            actual_url = unquote(match.group(1))
                            if 'illawarramercury.com.au/story/' in actual_url:
                                clean_url = actual_url.split('#')[0].split('?')[0]
                                if clean_url not in seen_urls:
                                    seen_urls.add(clean_url)
                                    urls.append(clean_url)
                                    found_in_this_search += 1
                                    print(f"  Found: {clean_url}")
                                    if len(urls) >= max_results:
                                        break
                
                print(f"Found {found_in_this_search} new articles with this query")
            else:
                print(f"Failed with status: {resp.status_code}")
                
        except Exception as e:
            print(f"Error with query '{search_query}': {e}")
        
        if len(urls) >= max_results:
            break
        
        time.sleep(2)  # Delay between searches
    
    print(f"\nTotal Google search results: {len(urls)} articles")
    
    # Test fetching a few articles to verify they work
    if urls:
        print(f"\nTesting article fetching...")
        for i, url in enumerate(urls[:5], 1):
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')
                    
                    title_elem = soup.find('h1')
                    title = title_elem.get_text().strip() if title_elem else "No title"
                    
                    date_elem = soup.find('time')
                    date = date_elem.get('datetime', '') if date_elem else ""
                    
                    print(f"{i}. {title}")
                    print(f"   URL: {url}")
                    if date:
                        print(f"   Date: {date}")
                    print()
                else:
                    print(f"{i}. Failed to fetch: {url} (Status: {resp.status_code})")
                    
            except Exception as e:
                print(f"{i}. Error fetching {url}: {e}")
    else:
        print("No articles found to test.")

if __name__ == "__main__":
    test_enhanced_google_search()
