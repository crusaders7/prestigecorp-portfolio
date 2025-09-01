#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


def test_enhanced_shellharbour_search():
    """Test enhanced search for various shellharbour council terms"""
    print("Testing enhanced search for various Shellharbour Council terms...")

    test_queries = [
        "shellharbour council",
        "Shellharbour Council",
        "shellharbour city council",
        "Shellharbour City Council",
        "shell harbour council"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: '{query}'")
        print('='*60)

        start_time = time.time()

        # Direct implementation of enhanced search
        urls = []
        seen_urls = set()
        max_results = 20

        # Search categories (enhanced list)
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
                        # Remove comments and fragments for deduplication
                        clean_url = full_url.split('#')[0].split('?')[0]
                        if clean_url not in seen_urls:
                            all_story_urls.append(clean_url)
                            seen_urls.add(clean_url)
            except Exception as e:
                print(f"Error processing {category_url}: {e}")
                continue

        print(f"Found {len(all_story_urls)} total articles to search")

        # Enhanced URL and content scoring
        query_lower = query.lower()
        query_words = [word.lower() for word in query.split() if len(word) > 2]

        # Create variations for better matching
        query_variations = [
            query_lower,
            query_lower.replace(' ', '-'),
            query_lower.replace(' ', '_'),
            query_lower.replace('council', 'city-council'),
            query_lower.replace('council', 'city_council'),
        ]

        if 'shellharbour' in query_lower:
            query_variations.extend([
                'shellharbour-city-council',
                'shell-harbour-council',
                'shell-harbour'
            ])

        # Show first few
        print(f"Search variations: {query_variations[:3]}...")

        # Content analysis with enhanced scoring
        title_matches = []
        articles_to_check = min(100, len(all_story_urls)
                                )  # Check more articles

        for i, story_url in enumerate(all_story_urls[:articles_to_check]):
            try:
                resp = requests.get(story_url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')

                    # Get title, meta description, and first paragraph
                    title_text = ""
                    title_elem = soup.find('h1')
                    if title_elem:
                        title_text = title_elem.get_text().lower()

                    meta_desc = ""
                    meta_elem = soup.find('meta', {'name': 'description'})
                    if meta_elem:
                        meta_desc = meta_elem.get('content', '').lower()

                    first_para = ""
                    para_elem = soup.find('p')
                    if para_elem:
                        first_para = para_elem.get_text()[:200].lower()

                    combined_text = f"{title_text} {meta_desc} {first_para}"

                    # Scoring
                    content_score = 0

                    # Check for query variations
                    for variation in query_variations:
                        if variation in combined_text:
                            content_score += 25
                            break

                    # Check exact phrase
                    if query_lower in combined_text:
                        content_score += 20

                    # Special Shellharbour handling
                    if 'shellharbour' in query_lower:
                        shellharbour_variants = [
                            'shellharbour', 'shell harbour', 'shell-harbour']
                        council_variants = ['council',
                                            'city council', 'city-council']

                        has_location = any(
                            variant in combined_text for variant in shellharbour_variants)
                        has_council = any(
                            variant in combined_text for variant in council_variants)

                        if has_location and has_council:
                            content_score += 15
                        elif has_location:
                            content_score += 8

                    # Check individual words
                    words_found = 0
                    for word in query_words:
                        if word in combined_text:
                            content_score += 5
                            words_found += 1
                            if word in title_text:
                                content_score += 3

                    if len(query_words) > 1 and words_found > 1:
                        content_score += words_found * 3

                    if content_score > 0:
                        title_matches.append(
                            (content_score, story_url, title_text))

                        # Show progress for longer searches
                        if len(title_matches) % 5 == 0:
                            print(
                                f"Found {len(title_matches)} matches so far... (checked {i+1}/{articles_to_check})")

                        if len(title_matches) >= max_results:
                            break

            except Exception:
                continue

        # Sort by score
        title_matches.sort(reverse=True, key=lambda x: x[0])

        end_time = time.time()
        duration = end_time - start_time

        print(
            f"\nResults for '{query}': {len(title_matches)} articles in {duration:.1f} seconds")

        if title_matches:
            print(
                f"Top scores: {[score for score, url, title in title_matches[:5]]}")
            print("\nTop articles:")
            for i, (score, url, title) in enumerate(title_matches[:8], 1):
                print(f"{i}. {title[:80]}... (Score: {score})")
                print(f"   URL: {url}")
                print()
        else:
            print("No articles found.")

        time.sleep(1)  # Brief pause between queries


if __name__ == "__main__":
    test_enhanced_shellharbour_search()
