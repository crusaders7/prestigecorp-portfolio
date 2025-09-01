#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import time
import random


def test_random_user_agents():
    """Test the search with random user agents"""
    print("Testing search with random user agents for 'shellharbour council'...")

    # Simulate the random user agent function
    def get_random_user_agent():
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)

    query = "shellharbour council"
    max_results = 10

    # Test category scraping with random user agents
    category_urls = [
        "https://www.illawarramercury.com.au",
        "https://www.illawarramercury.com.au/news/",
        "https://www.illawarramercury.com.au/news/local-news/"
    ]

    all_story_urls = []
    seen_urls = set()

    print("Testing category scraping with random user agents...")
    for i, category_url in enumerate(category_urls, 1):
        user_agent = get_random_user_agent()
        print(f"\n{i}. Trying {category_url}")
        print(f"   User Agent: {user_agent[:50]}...")

        try:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }

            resp = requests.get(category_url, headers=headers, timeout=12)
            print(f"   Status: {resp.status_code}")

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')

                category_stories = 0
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/story/' in href:
                        full_url = urljoin(
                            "https://www.illawarramercury.com.au", href)
                        clean_url = full_url.split('#')[0].split('?')[0]
                        if clean_url not in seen_urls:
                            all_story_urls.append(clean_url)
                            seen_urls.add(clean_url)
                            category_stories += 1

                print(f"   Found {category_stories} new stories")
            else:
                print(f"   Failed with status {resp.status_code}")

        except Exception as e:
            print(f"   Error: {e}")

        time.sleep(1)  # Small delay between requests

    print(f"\nTotal stories collected: {len(all_story_urls)}")

    # Test content analysis with random user agents for some articles
    if all_story_urls:
        print(f"\nTesting content analysis with random user agents...")
        matches = []

        for i, story_url in enumerate(all_story_urls[:20], 1):  # Test first 20
            user_agent = get_random_user_agent()

            try:
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Connection': 'keep-alive'
                }

                resp = requests.get(story_url, headers=headers, timeout=8)

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')

                    title_elem = soup.find('h1')
                    title = title_elem.get_text().lower() if title_elem else ""

                    # Check for shellharbour + council
                    if 'shellharbour' in title and 'council' in title:
                        matches.append({
                            'url': story_url,
                            'title': title_elem.get_text().strip() if title_elem else "No title",
                            'user_agent': user_agent[:30] + "..."
                        })
                        print(f"   MATCH {len(matches)}: {title[:60]}...")

                if i % 5 == 0:
                    print(
                        f"   Checked {i}/20 articles, found {len(matches)} matches")

            except Exception as e:
                continue

            time.sleep(0.3)  # Small delay

    print(f"\n{'='*60}")
    print(f"FINAL RESULTS with Random User Agents")
    print(f"Found {len(matches)} Shellharbour Council articles")
    print('='*60)

    if matches:
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match['title']}")
            print(f"   URL: {match['url']}")
            print(f"   Used UA: {match['user_agent']}")
    else:
        print("No Shellharbour Council articles found in sample.")
        print("This suggests either:")
        print("1. No recent articles in the feeds we checked")
        print("2. Need to check more categories or older articles")
        print("3. Different search strategies needed")


if __name__ == "__main__":
    test_random_user_agents()
