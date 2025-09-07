#!/usr/bin/env python3
"""
Test the optimized search functionality
"""
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, unquote
import time
import re

# Copy the optimized search function to test it


def search_illawarra_mercury_optimized(query, max_results):
    """
    Optimized search focusing on relevance and speed
    """
    print(f"Searching Illawarra Mercury for '{query}'...")

    urls = []
    seen_urls = set()

    try:
        category_urls = [
            "https://www.illawarramercury.com.au",
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/news/business/"
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        all_story_urls = []

        for category_url in category_urls:
            try:
                resp = requests.get(category_url, headers=headers, timeout=12)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, 'lxml')

                # Find all story links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/story/' in href:
                        full_url = urljoin(
                            "https://www.illawarramercury.com.au", href)
                        # Remove comment links and duplicates
                        if '#comments' not in full_url and full_url not in all_story_urls:
                            all_story_urls.append(full_url)

            except Exception as e:
                print(f"Failed to scrape category {category_url}: {e}")
                continue

        print(f"Found {len(all_story_urls)} total articles from categories")

        # URL keyword matching with scoring
        query_words = [word.lower() for word in query.split() if len(word) > 2]

        # Score URLs based on relevance
        url_scores = []
        for story_url in all_story_urls:
            url_text = story_url.lower()
            score = 0

            # Higher score for exact matches in URL
            for word in query_words:
                if word in url_text:
                    score += 10
                    # Bonus for word appearing in the story slug
                    if '/story/' in url_text and word in url_text.split('/story/')[-1]:
                        score += 5

            if score > 0:
                url_scores.append((score, story_url))

        # Sort by relevance score and take top results
        url_scores.sort(reverse=True, key=lambda x: x[0])
        relevant_urls = [url for score, url in url_scores[:max_results]]

        print(f"Found {len(relevant_urls)} relevant URL matches")

        if relevant_urls:
            return relevant_urls

        print("No URL matches found - query may be too specific")
        return []

    except Exception as e:
        print(f"Search failed: {e}")
        return []


def test_optimized_search():
    print("Testing optimized search functionality...")

    # Test with different queries
    test_queries = [
        "council",
        "sport",
        "business",
        "shellharbour",
        "wollongong",
        "football"
    ]

    for query in test_queries:
        print(f"\n=== Testing query: '{query}' ===")
        start_time = time.time()
        try:
            urls = search_illawarra_mercury_optimized(query, 10)
            end_time = time.time()

            print(
                f"Found {len(urls)} articles for '{query}' in {end_time - start_time:.1f} seconds")

            # Show first 3 URLs
            for i, url in enumerate(urls[:3], 1):
                print(f"  {i}. {url}")

            if len(urls) > 3:
                print(f"  ... and {len(urls) - 3} more articles")

        except Exception as e:
            print(f"Error testing '{query}': {e}")


if __name__ == "__main__":
    test_optimized_search()
