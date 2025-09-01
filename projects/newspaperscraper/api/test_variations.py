#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import time
import re


def test_searches():
    """Test multiple search variations"""

    searches = [
        "shellharbour council",
        "shellharbour",
        "shell cove"
    ]

    for query in searches:
        print(f"\n{'='*50}")
        print(f"Testing search for: '{query}'")
        print('='*50)

        start_time = time.time()

        # Direct implementation of search
        urls = []
        seen_urls = set()

        # Search categories
        category_urls = [
            "https://www.illawarramercury.com.au",
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/news/business/",
            "https://www.illawarramercury.com.au/news/local-news/",
            "https://www.illawarramercury.com.au/news/politics/"
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        all_story_urls = []

        # Collect all story URLs
        for category_url in category_urls:
            try:
                resp = requests.get(category_url, headers=headers, timeout=12)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, 'lxml')

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/story/' in href:
                        full_url = urljoin(
                            "https://www.illawarramercury.com.au", href)
                        clean_url = full_url.split('#')[0].split('?')[0]
                        if clean_url not in seen_urls:
                            all_story_urls.append(clean_url)
                            seen_urls.add(clean_url)
            except Exception as e:
                print(f"Error processing {category_url}: {e}")
                continue

        print(f"Found {len(all_story_urls)} total articles to search")

        # Enhanced URL scoring
        query_words = [word.lower() for word in query.split() if len(word) > 2]
        print(f"Search words: {query_words}")

        url_scores = []
        for story_url in all_story_urls:
            url_text = story_url.lower()
            score = 0

            # Check for exact phrase match
            if query.lower().replace(' ', '-') in url_text:
                score += 25

            # Check individual words
            words_found = 0
            for word in query_words:
                if word in url_text:
                    score += 10
                    words_found += 1
                    if '/story/' in url_text and word in url_text.split('/story/')[-1]:
                        score += 5

            # Bonus for multiple words
            if len(query_words) > 1 and words_found > 1:
                score += words_found * 3

            if score > 0:
                url_scores.append((score, story_url))

        url_scores.sort(reverse=True, key=lambda x: x[0])
        print(f"Found {len(url_scores)} URL matches")

        # Get articles from top URLs
        results = []
        for score, url in url_scores[:10]:  # Top 10 results
            try:
                resp = requests.get(url, headers=headers, timeout=8)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')

                    title_elem = soup.find('h1')
                    title = title_elem.get_text().strip() if title_elem else "No title"

                    date_elem = soup.find('time')
                    date = date_elem.get('datetime', '') if date_elem else ""

                    results.append({
                        'title': title,
                        'url': url,
                        'date': date,
                        'source': 'Illawarra Mercury',
                        'relevance_score': score
                    })
            except Exception as e:
                continue

        end_time = time.time()
        duration = end_time - start_time

        print(f"Found {len(results)} articles in {duration:.1f} seconds")

        if results:
            print("\nTop results:")
            for i, article in enumerate(results[:5], 1):  # Show top 5
                print(
                    f"{i}. {article.get('title', 'No title')} (Score: {article.get('relevance_score', 0)})")
                print(f"   Date: {article.get('date', 'No date')}")
                print()
        else:
            print("No articles found.")

        time.sleep(2)  # Brief pause between searches


if __name__ == "__main__":
    test_searches()
