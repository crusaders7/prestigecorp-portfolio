#!/usr/bin/env python3
"""
PERFECT MATCH SEARCH SYSTEM
Integrates enhanced discovery methods into the main search for perfect matches
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime
import sys


class PerfectMatchSearchSystem:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # All 69 discovered working categories
        self.comprehensive_categories = [
            'https://www.illawarramercury.com.au/www.illawarramercury.com.au',
            'https://www.illawarramercury.com.au/sport',
            'https://www.illawarramercury.com.au/entertainment',
            'https://www.illawarramercury.com.au/news',
            'https://www.illawarramercury.com.au/lifestyle',
            'https://www.illawarramercury.com.au/business',
            'https://www.illawarramercury.com.au/environment',
            'https://www.illawarramercury.com.au/local-news',
            'https://www.illawarramercury.com.au/basketball',
            'https://www.illawarramercury.com.au/education',
            'https://www.illawarramercury.com.au/health',
            'https://www.illawarramercury.com.au/politics',
            'https://www.illawarramercury.com.au/cricket',
            'https://www.illawarramercury.com.au/community',
            'https://www.illawarramercury.com.au/national-sport',
            'https://www.illawarramercury.com.au/car-expert',
            'https://www.illawarramercury.com.au/food-drink',
            'https://www.illawarramercury.com.au/your-news',
            'https://www.illawarramercury.com.au/home-garden',
            'https://www.illawarramercury.com.au/babies-weddings-obituaries',
            'https://www.illawarramercury.com.au/parenting',
            'https://www.illawarramercury.com.au/history',
            'https://www.illawarramercury.com.au/money',
            'https://www.illawarramercury.com.au/local-league',
            'https://www.illawarramercury.com.au/hawks-nest',
            'https://www.illawarramercury.com.au/movies',
            'https://www.illawarramercury.com.au/local-sport',
            'https://www.illawarramercury.com.au/dragons-den',
            'https://www.illawarramercury.com.au/court-crime',
            'https://www.illawarramercury.com.au/pets-animals',
            'https://www.illawarramercury.com.au/health-wellbeing',
            'https://www.illawarramercury.com.au/junior-sport',
            'https://www.illawarramercury.com.au/books',
            'https://www.illawarramercury.com.au/toyota-hub',
            'https://www.illawarramercury.com.au/national',
            'https://www.illawarramercury.com.au/arts-and-theatre',
            'https://www.illawarramercury.com.au/recipes',
            'https://www.illawarramercury.com.au/music',
        ]

    def enhanced_story_id_discovery(self, query_terms):
        """Enhanced story ID discovery based on content analysis"""
        print("\n🎯 ENHANCED STORY ID DISCOVERY")
        print("=" * 50)

        found_articles = []

        # Get current story ID range from RSS
        try:
            response = requests.get(
                'https://www.illawarramercury.com.au/rss.xml', headers=self.headers)
            if response.status_code == 200:
                content = response.text
                story_urls = re.findall(
                    r'https://www\.illawarramercury\.com\.au/story/(\d+)/', content)
                rss_ids = [int(id_str) for id_str in story_urls]

                if rss_ids:
                    min_id = min(rss_ids)
                    max_id = max(rss_ids)
                    print(f"📊 Current ID range: {min_id} - {max_id}")

                    # Sample scan around the range for relevant content
                    sample_ranges = [
                        (max_id - 100, max_id),  # Recent articles
                        (min_id, min_id + 100),  # Older articles
                        (max_id - 1000, max_id - 900),  # Mid-range sample
                    ]

                    print(f"🔍 Scanning for articles matching: {query_terms}")

                    for start_id, end_id in sample_ranges:
                        print(f"\n📊 Scanning range {start_id} - {end_id}:")

                        # Sample every 5th ID to avoid overwhelming
                        for story_id in range(start_id, end_id, 5):
                            try:
                                story_url = f"https://www.illawarramercury.com.au/story/{story_id}/"
                                response = requests.get(
                                    story_url, headers=self.headers, timeout=5)

                                if response.status_code == 200:
                                    soup = BeautifulSoup(
                                        response.content, 'html.parser')

                                    # Get title and content
                                    title_elem = soup.find(
                                        'h1') or soup.find('title')
                                    title = title_elem.get_text(
                                        strip=True) if title_elem else ""

                                    # Get first paragraph for content analysis
                                    content_elem = soup.find('p')
                                    content = content_elem.get_text(
                                        strip=True) if content_elem else ""

                                    # Calculate relevance score
                                    relevance_score = 0
                                    text_to_analyze = (
                                        title + " " + content).lower()

                                    for term in query_terms:
                                        if term.lower() in text_to_analyze:
                                            relevance_score += 1

                                    if relevance_score >= 1:
                                        print(
                                            f"   🎯 {story_id}: Score {relevance_score} - {title[:60]}...")
                                        found_articles.append({
                                            'id': story_id,
                                            'url': story_url,
                                            'title': title,
                                            'score': relevance_score
                                        })

                                # Rate limiting
                                time.sleep(0.1)

                            except Exception:
                                continue

        except Exception as e:
            print(f"❌ Error in story ID discovery: {str(e)}")

        return found_articles

    def comprehensive_category_scan(self, query_terms, max_articles_per_category=100):
        """Comprehensive scan of all 69 categories with enhanced extraction"""
        print("\n📂 COMPREHENSIVE CATEGORY SCANNING")
        print("=" * 50)

        all_articles = []
        relevant_articles = []

        for i, category in enumerate(self.comprehensive_categories):
            print(f"\n📂 [{i+1}/69] Scanning: {category}")

            try:
                response = requests.get(
                    category, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Enhanced article extraction
                    article_links = set()

                    # Method 1: Standard link extraction
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href and 'illawarramercury.com.au' in href:
                            if not href.startswith('http'):
                                href = 'https://www.illawarramercury.com.au' + href
                            article_links.add(href)

                    # Method 2: Data attributes
                    for element in soup.find_all(attrs={'data-url': True}):
                        data_url = element['data-url']
                        if '/story/' in data_url:
                            if not data_url.startswith('http'):
                                data_url = 'https://www.illawarramercury.com.au' + data_url
                            article_links.add(data_url)

                    # Method 3: JavaScript/JSON content
                    for script in soup.find_all('script'):
                        if script.string:
                            story_urls = re.findall(
                                r'https://www\.illawarramercury\.com\.au/story/\d+/[^"\']+', script.string)
                            article_links.update(story_urls)

                    category_articles = list(article_links)[
                        :max_articles_per_category]

                    if category_articles:
                        print(f"   ✅ Found {len(category_articles)} articles")
                        all_articles.extend(category_articles)

                        # Quick relevance check on titles from URLs
                        relevant_count = 0
                        for article_url in category_articles:
                            relevance_score = 0
                            for term in query_terms:
                                if term.lower() in article_url.lower():
                                    relevance_score += 1

                            if relevance_score > 0:
                                relevant_count += 1
                                relevant_articles.append({
                                    'url': article_url,
                                    'category': category,
                                    'score': relevance_score
                                })

                        if relevant_count > 0:
                            print(
                                f"   🎯 {relevant_count} potentially relevant articles")
                    else:
                        print(f"   📄 No articles found")
                else:
                    print(f"   ❌ Status: {response.status_code}")

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

            time.sleep(0.3)  # Rate limiting

        return all_articles, relevant_articles

    def perfect_match_search(self, query="shellharbour council"):
        """Execute perfect match search with all enhancement methods"""
        print("🎯 PERFECT MATCH SEARCH SYSTEM")
        print("=" * 60)
        print(f"🔍 Query: '{query}'")
        print("=" * 60)

        query_terms = query.lower().split()
        all_results = {
            'total_articles': 0,
            'relevant_articles': [],
            'story_id_matches': [],
            'category_matches': [],
            'perfect_matches': []
        }

        # Phase 1: Enhanced Story ID Discovery
        print("\n📊 PHASE 1: ENHANCED STORY ID DISCOVERY")
        story_matches = self.enhanced_story_id_discovery(query_terms)
        all_results['story_id_matches'] = story_matches

        # Phase 2: Comprehensive Category Scanning
        print("\n📊 PHASE 2: COMPREHENSIVE CATEGORY SCANNING")
        all_articles, relevant_articles = self.comprehensive_category_scan(
            query_terms)
        all_results['total_articles'] = len(set(all_articles))
        all_results['category_matches'] = relevant_articles

        # Phase 3: Perfect Match Identification
        print("\n📊 PHASE 3: PERFECT MATCH IDENTIFICATION")
        perfect_matches = []

        # Combine all relevant findings
        all_relevant = []

        # Add story ID matches
        for match in story_matches:
            all_relevant.append({
                'url': match['url'],
                'title': match['title'],
                'score': match['score'] + 5,  # Bonus for content-based match
                'source': 'story_id_scan'
            })

        # Add category matches
        for match in relevant_articles:
            all_relevant.append({
                'url': match['url'],
                'title': 'Category match',
                'score': match['score'],
                'source': f"category: {match['category']}"
            })

        # Sort by relevance score
        all_relevant.sort(key=lambda x: x['score'], reverse=True)

        # Identify perfect matches (high score articles)
        for article in all_relevant:
            if article['score'] >= 2:  # High relevance threshold
                perfect_matches.append(article)

        all_results['perfect_matches'] = perfect_matches
        all_results['relevant_articles'] = all_relevant

        return all_results

    def print_results(self, results):
        """Print comprehensive results"""
        print("\n" + "=" * 60)
        print("🎯 PERFECT MATCH SEARCH RESULTS")
        print("=" * 60)

        print(f"📊 Total articles scanned: {results['total_articles']}")
        print(f"🔍 Story ID matches: {len(results['story_id_matches'])}")
        print(f"📂 Category matches: {len(results['category_matches'])}")
        print(f"⭐ Perfect matches: {len(results['perfect_matches'])}")
        print(f"📝 Total relevant: {len(results['relevant_articles'])}")

        if results['perfect_matches']:
            print(f"\n⭐ PERFECT MATCHES (Score ≥ 2):")
            for i, match in enumerate(results['perfect_matches'][:10], 1):
                print(
                    f"   {i}. Score {match['score']}: {match['title'][:60]}...")
                print(f"      Source: {match['source']}")
                print(f"      URL: {match['url']}")
                print()

        if results['story_id_matches']:
            print(f"\n🎯 STORY ID DISCOVERY HIGHLIGHTS:")
            for match in results['story_id_matches'][:5]:
                print(f"   • ID {match['id']}: {match['title'][:60]}...")
                print(f"     Score: {match['score']}")

        print(f"\n✅ SEARCH COMPLETE!")
        print(
            f"💡 Found {len(results['perfect_matches'])} perfect matches for enhanced targeting!")


def main():
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = "shellharbour council"

    search_system = PerfectMatchSearchSystem()
    results = search_system.perfect_match_search(query)
    search_system.print_results(results)


if __name__ == "__main__":
    main()
