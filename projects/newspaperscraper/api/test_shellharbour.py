#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import time
import re


def test_shellharbour_search():
    """Test search for shellharbour council articles"""
    print("Testing enhanced search for 'shellharbour council'...")
    start_time = time.time()

    query = "shellharbour council"
    max_results = 20

    # Direct implementation of enhanced search
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
                    # Remove comments/fragments and query params for clean deduplication
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

        # Special handling for compound terms
        if len(query_words) == 2:
            story_part = url_text.split(
                '/story/')[-1] if '/story/' in url_text else url_text
            if any(word in story_part for word in query_words):
                score += 8

        if score > 0:
            url_scores.append((score, story_url))

    url_scores.sort(reverse=True, key=lambda x: x[0])
    print(f"Found {len(url_scores)} URL matches")

    if url_scores:
        print(f"Top 5 scores: {[score for score, url in url_scores[:5]]}")
        for score, url in url_scores[:3]:
            print(f"  Score {score}: {url}")

    # Get articles from top URLs
    results = []
    for score, url in url_scores[:max_results]:
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
            print(f"Error fetching {url}: {e}")
            continue

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n=== Search Results for 'shellharbour council' ===")
    print(f"Found {len(results)} articles in {duration:.1f} seconds")

    if results:
        print("\nArticle titles:")
        for i, article in enumerate(results, 1):
            print(
                f"{i}. {article.get('title', 'No title')} (Score: {article.get('relevance_score', 0)})")
            print(f"   URL: {article.get('url', 'No URL')}")
            if article.get('date'):
                print(f"   Date: {article.get('date')}")
            print()
    else:
        print("No articles found.")

    return results


if __name__ == "__main__":
    test_shellharbour_search()
