#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re


def quick_shellharbour_test():
    """Quick test to find Shellharbour Council articles with enhanced patterns"""

    print("Quick search for Shellharbour Council articles...")
    start_time = time.time()

    query = "shellharbour council"
    max_results = 20

    # Enhanced categories
    category_urls = [
        "https://www.illawarramercury.com.au",
        "https://www.illawarramercury.com.au/news/",
        "https://www.illawarramercury.com.au/news/local-news/",
        "https://www.illawarramercury.com.au/news/politics/",
        "https://www.illawarramercury.com.au/news/business/"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Collect URLs
    all_story_urls = []
    seen_urls = set()

    for category_url in category_urls:
        try:
            resp = requests.get(category_url, headers=headers, timeout=10)
            if resp.status_code == 200:
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
            print(f"Error with {category_url}: {e}")
            continue

    print(f"Collected {len(all_story_urls)} articles to check")

    # Enhanced search patterns
    shellharbour_patterns = [
        r'shellharbour\s+council',
        r'shellharbour\s+city\s+council',
        r'shell\s+harbour\s+council',
        r'shellharbour-council',
        r'shellharbour-city-council'
    ]

    matches = []
    checked = 0

    # Check first 150 articles more thoroughly
    for story_url in all_story_urls[:150]:
        checked += 1
        if checked % 25 == 0:
            print(
                f"Checked {checked}/150 articles, found {len(matches)} matches so far...")

        try:
            resp = requests.get(story_url, headers=headers, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')

                # Get full content for thorough check
                title_elem = soup.find('h1')
                title = title_elem.get_text() if title_elem else ""

                # Get article body content
                body_content = ""
                for selector in ['.story-content', '.article-content', '.entry-content', 'article']:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        body_content = content_elem.get_text()
                        break

                if not body_content:
                    # Fallback to all paragraphs
                    paragraphs = soup.find_all('p')
                    body_content = ' '.join([p.get_text()
                                            for p in paragraphs[:5]])

                full_text = f"{title} {body_content}".lower()

                # Check for shellharbour patterns
                score = 0
                found_patterns = []

                for pattern in shellharbour_patterns:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        score += 10
                        found_patterns.append(pattern)

                # Additional scoring
                if 'shellharbour' in full_text and 'council' in full_text:
                    score += 5

                if 'shellharbour' in title.lower():
                    score += 8

                if 'council' in title.lower():
                    score += 5

                if score > 0:
                    matches.append({
                        'title': title,
                        'url': story_url,
                        'score': score,
                        'patterns': found_patterns
                    })

        except Exception:
            continue

        time.sleep(0.1)  # Small delay

    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n{'='*60}")
    print(f"ENHANCED SEARCH RESULTS for 'shellharbour council'")
    print(f"Found {len(matches)} relevant articles in {duration:.1f} seconds")
    print(f"Checked {checked} articles total")
    print('='*60)

    if matches:
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match['title']} (Score: {match['score']})")
            print(f"   URL: {match['url']}")
            if match['patterns']:
                print(f"   Matched patterns: {', '.join(match['patterns'])}")
    else:
        print("No specific Shellharbour Council articles found.")
        print("This might indicate that:")
        print("1. Articles use different terminology")
        print("2. Articles are older and not in recent feeds")
        print("3. Articles might be in sections we're not checking")


if __name__ == "__main__":
    quick_shellharbour_test()
