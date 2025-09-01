#!/usr/bin/env python3
"""
Test the improved search functionality
"""
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, unquote
import time
import re

# Copy the improved search function directly to test it


def search_illawarra_mercury_improved(query, max_results):
    """
    Searches the Illawarra Mercury website using a multi-strategy approach.
    Uses homepage/category scraping as primary method since search is unreliable.
    """
    print(f"Searching Illawarra Mercury for '{query}'...")

    urls = []
    seen_urls = set()

    # Strategy 1: Homepage and category scraping (most reliable)
    try:
        category_urls = [
            "https://www.illawarramercury.com.au",
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/news/local/",
            "https://www.illawarramercury.com.au/news/business/",
            "https://www.illawarramercury.com.au/news/national/",
            "https://www.illawarramercury.com.au/lifestyle/",
            "https://www.illawarramercury.com.au/entertainment/",
            "https://www.illawarramercury.com.au/opinion/"
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

                # Find all story links with more comprehensive search
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

        # Strategy 1a: First try exact keyword matching in URLs
        query_words = [word.lower() for word in query.split()
                       if len(word) > 2]  # Skip short words
        exact_matches = []

        for story_url in all_story_urls:
            url_text = story_url.lower()
            # Check if URL contains any of the query words
            if any(word in url_text for word in query_words):
                exact_matches.append(story_url)

        print(f"Found {len(exact_matches)} exact URL matches")

        # Strategy 1b: If we have exact matches but not enough, also do content-based search
        if len(exact_matches) > 0:
            urls.extend(exact_matches[:max_results])
            seen_urls.update(exact_matches[:max_results])

        # Strategy 1c: If still need more results, try content analysis on article titles/previews
        if len(urls) < max_results and len(all_story_urls) > len(exact_matches):
            print("Analyzing article content for additional matches...")

            content_matches = []
            articles_to_check = [
                url for url in all_story_urls if url not in seen_urls]

            # Check up to 20 articles for content matches to avoid being too slow
            for story_url in articles_to_check[:min(20, len(articles_to_check))]:
                try:
                    resp = requests.get(story_url, headers=headers, timeout=8)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.content, 'lxml')

                        # Get title and meta description
                        title_text = ""
                        title_elem = soup.find('h1')
                        if title_elem:
                            title_text = title_elem.get_text().lower()

                        meta_desc = ""
                        meta_elem = soup.find('meta', {'name': 'description'})
                        if meta_elem:
                            meta_desc = meta_elem.get('content', '').lower()

                        # Check if query words appear in title or description
                        combined_text = f"{title_text} {meta_desc}"
                        if any(word in combined_text for word in query_words):
                            content_matches.append(story_url)
                            if len(content_matches) >= (max_results - len(urls)):
                                break

                except Exception as e:
                    # Skip articles that fail to load
                    continue

                # Small delay to be respectful
                time.sleep(0.5)

            print(f"Found {len(content_matches)} additional content matches")

            # Add content matches
            remaining_slots = max_results - len(urls)
            urls.extend(content_matches[:remaining_slots])
            seen_urls.update(content_matches[:remaining_slots])

        # Strategy 1d: If still not enough results, add most recent articles
        if len(urls) < max_results:
            remaining_slots = max_results - len(urls)
            recent_articles = [
                url for url in all_story_urls if url not in seen_urls]
            urls.extend(recent_articles[:remaining_slots])
            seen_urls.update(recent_articles[:remaining_slots])
            print(
                f"Added {min(remaining_slots, len(recent_articles))} recent articles to fill quota")

        if urls:
            print(f"Strategy 1 found {len(urls)} total articles")
            return urls

    except Exception as e:
        print(f"Homepage scraping failed: {e}")

    print(f"Final result: {len(urls)} articles found")
    return urls[:max_results]


def test_improved_search():
    print("Testing improved search functionality...")

    # Test with different queries
    test_queries = [
        "council",
        "sport"
    ]

    for query in test_queries:
        print(f"\n=== Testing query: '{query}' ===")
        try:
            urls = search_illawarra_mercury_improved(
                query, 15)  # Ask for up to 15 results
            print(f"Found {len(urls)} articles for '{query}'")

            # Show first 5 URLs
            for i, url in enumerate(urls[:5], 1):
                print(f"  {i}. {url}")

            if len(urls) > 5:
                print(f"  ... and {len(urls) - 5} more articles")

        except Exception as e:
            print(f"Error testing '{query}': {e}")


if __name__ == "__main__":
    test_improved_search()
