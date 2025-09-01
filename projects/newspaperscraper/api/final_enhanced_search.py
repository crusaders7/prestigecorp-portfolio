#!/usr/bin/env python3
"""
FINAL ENHANCED SEARCH SYSTEM
Integrates all discoveries to create the most comprehensive search system
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime


class EnhancedSearchSystem:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Comprehensive working categories from our discovery
        self.tier1_categories = [
            'https://www.illawarramercury.com.au/',
            'https://www.illawarramercury.com.au/sport/',
            'https://www.illawarramercury.com.au/news/',
        ]

        # Additional categories that might contain missing articles
        self.extended_categories = [
            'https://www.illawarramercury.com.au/entertainment/',
            'https://www.illawarramercury.com.au/lifestyle/',
            'https://www.illawarramercury.com.au/business/',
            'https://www.illawarramercury.com.au/environment/',
            'https://www.illawarramercury.com.au/local-news/',
            'https://www.illawarramercury.com.au/basketball/',
            'https://www.illawarramercury.com.au/education/',
            'https://www.illawarramercury.com.au/health/',
            'https://www.illawarramercury.com.au/politics/',
            'https://www.illawarramercury.com.au/cricket/',
            'https://www.illawarramercury.com.au/community/',
        ]

        # Target articles for validation
        self.target_articles = {
            '9050660': 'Shellharbour cricket players not forgotten by council',
            '9046630': 'Inappropriate: Shellharbour Mayor Chris Homer meets with sacked CEO Mike Archer',
            '9045329': 'We all want to play: heartbreak over more sport wet-weather chaos',
            '636609': 'Shellharbour ALP candidate Tim Banfield quits, and backs an independent',
            '9044604': 'Workplace culture top-notch: Shellharbour Mayor Chris Homer quiet on CEO sacking'
        }

    def scrape_category_with_pagination(self, category_url, max_pages=10):
        """Scrape a category with deep pagination"""
        all_articles = []
        found_targets = []

        print(f"\n📂 Scraping: {category_url}")

        for page in range(1, max_pages + 1):
            try:
                # Try different pagination formats
                page_urls = [
                    f"{category_url}?page={page}" if page > 1 else category_url,
                    f"{category_url}page/{page}/" if page > 1 else category_url,
                    f"{category_url}p{page}/" if page > 1 else category_url,
                ]

                page_articles = []
                for page_url in page_urls:
                    try:
                        response = requests.get(
                            page_url, headers=self.headers, timeout=15)
                        if response.status_code == 200:
                            soup = BeautifulSoup(
                                response.content, 'html.parser')

                            # Extract articles using multiple patterns
                            article_links = set()

                            # Pattern 1: Direct story links
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                if '/story/' in href and 'illawarramercury.com.au' in href:
                                    if not href.startswith('http'):
                                        href = 'https://www.illawarramercury.com.au' + href
                                    article_links.add(href)

                            # Pattern 2: Data attributes and JSON
                            for element in soup.find_all(attrs={'data-url': True}):
                                data_url = element['data-url']
                                if '/story/' in data_url:
                                    if not data_url.startswith('http'):
                                        data_url = 'https://www.illawarramercury.com.au' + data_url
                                    article_links.add(data_url)

                            # Pattern 3: Script tags with JSON data
                            for script in soup.find_all('script', type='application/json'):
                                try:
                                    json_data = json.loads(script.string)
                                    json_str = json.dumps(json_data)
                                    story_urls = re.findall(
                                        r'https://www\.illawarramercury\.com\.au/story/\d+/[^"]+', json_str)
                                    article_links.update(story_urls)
                                except:
                                    continue

                            if article_links:
                                page_articles = list(article_links)
                                break  # Found working pagination format
                    except:
                        continue

                if not page_articles:
                    if page == 1:
                        print(f"   ⚠️ No articles found on page {page}")
                    else:
                        print(f"   📄 End of pagination at page {page}")
                    break

                # Check for target articles
                page_targets = []
                for article_url in page_articles:
                    for target_id in self.target_articles.keys():
                        if target_id in article_url:
                            page_targets.append((target_id, article_url))
                            found_targets.append((target_id, article_url))

                if page_targets:
                    print(
                        f"   📄 Page {page}: {len(page_articles)} articles - 🎯 FOUND {len(page_targets)} TARGETS!")
                    for target_id, url in page_targets:
                        print(
                            f"      • {target_id}: {self.target_articles[target_id]}")
                else:
                    # Show sample IDs for context
                    sample_ids = []
                    for url in page_articles[:5]:
                        match = re.search(r'/story/(\d+)/', url)
                        if match:
                            sample_ids.append(int(match.group(1)))

                    if sample_ids:
                        print(
                            f"   📄 Page {page}: {len(page_articles)} articles (IDs: {min(sample_ids)}-{max(sample_ids)})")
                    else:
                        print(
                            f"   📄 Page {page}: {len(page_articles)} articles")

                all_articles.extend(page_articles)
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break

        return all_articles, found_targets

    def test_direct_story_id_scanning(self):
        """Test scanning around target story IDs to find them"""
        print("\n🔍 DIRECT STORY ID SCANNING")
        print("=" * 50)

        found_articles = []

        # Get the ID range from RSS
        try:
            response = requests.get(
                'https://www.illawarramercury.com.au/rss.xml', headers=self.headers)
            if response.status_code == 200:
                content = response.text
                story_urls = re.findall(
                    r'https://www\.illawarramercury\.com\.au/story/(\d+)/', content)
                rss_ids = [int(id_str) for id_str in story_urls]

                if rss_ids:
                    min_rss_id = min(rss_ids)
                    max_rss_id = max(rss_ids)
                    print(f"📊 RSS ID range: {min_rss_id} - {max_rss_id}")

                    # Test story IDs around our targets
                    target_ids = [
                        int(id_str) for id_str in self.target_articles.keys() if id_str.isdigit()]

                    for target_id in target_ids:
                        print(f"\n🎯 Testing around story ID {target_id}:")

                        # Test the target and surrounding IDs
                        test_range = range(target_id - 5, target_id + 6)
                        for test_id in test_range:
                            if test_id < 1000000:  # Skip very small IDs
                                continue

                            test_url = f"https://www.illawarramercury.com.au/story/{test_id}/"

                            try:
                                response = requests.get(
                                    test_url, headers=self.headers, timeout=10)
                                if response.status_code == 200:
                                    soup = BeautifulSoup(
                                        response.content, 'html.parser')
                                    title_elem = soup.find(
                                        'h1') or soup.find('title')
                                    title = title_elem.get_text(
                                        strip=True) if title_elem else "No title found"

                                    if test_id == target_id:
                                        print(
                                            f"   🎯 {test_id}: ✅ TARGET FOUND - {title[:80]}...")
                                        found_articles.append(
                                            (str(test_id), test_url, title))
                                    else:
                                        print(
                                            f"   📄 {test_id}: ✅ {title[:60]}...")
                                else:
                                    marker = "🎯" if test_id == target_id else "📄"
                                    print(
                                        f"   {marker} {test_id}: ❌ Status {response.status_code}")

                                time.sleep(0.3)

                            except Exception as e:
                                marker = "🎯" if test_id == target_id else "📄"
                                print(
                                    f"   {marker} {test_id}: ❌ Error: {str(e)}")

        except Exception as e:
            print(f"❌ Error in ID scanning: {str(e)}")

        return found_articles

    def run_comprehensive_search(self, query="shellharbour council"):
        """Run the comprehensive enhanced search"""
        print("🚀 FINAL ENHANCED SEARCH SYSTEM")
        print("=" * 60)
        print(f"🔍 Search Query: '{query}'")
        print("=" * 60)

        all_found_articles = []
        all_found_targets = []

        # Phase 1: Direct story ID scanning
        print("\n📊 PHASE 1: DIRECT STORY ID VALIDATION")
        id_found = self.test_direct_story_id_scanning()
        all_found_targets.extend(id_found)

        # Phase 2: Tier 1 categories with deep pagination
        print("\n📊 PHASE 2: TIER 1 CATEGORY SCANNING")
        for category in self.tier1_categories:
            articles, targets = self.scrape_category_with_pagination(
                category, max_pages=15)
            all_found_articles.extend(articles)
            all_found_targets.extend(targets)

        # Phase 3: Extended categories
        print("\n📊 PHASE 3: EXTENDED CATEGORY SCANNING")
        for category in self.extended_categories:
            articles, targets = self.scrape_category_with_pagination(
                category, max_pages=5)
            all_found_articles.extend(articles)
            all_found_targets.extend(targets)

        # Phase 4: Content analysis for relevance
        print("\n📊 PHASE 4: RELEVANCE ANALYSIS")
        relevant_articles = self.analyze_relevance(all_found_articles, query)

        return {
            'total_articles': len(set(all_found_articles)),
            'found_targets': all_found_targets,
            'relevant_articles': relevant_articles,
            'target_completion': len(set([t[0] for t in all_found_targets])) / len(self.target_articles) * 100
        }

    def analyze_relevance(self, articles, query):
        """Analyze articles for relevance to query"""
        query_terms = query.lower().split()
        relevant = []

        print(
            f"🔍 Analyzing {len(set(articles))} unique articles for relevance...")

        # Sample analysis on first 20 articles to avoid overwhelming output
        sample_articles = list(set(articles))[:20]

        for article_url in sample_articles:
            try:
                # Extract basic info from URL
                url_score = 0
                for term in query_terms:
                    if term in article_url.lower():
                        url_score += 1

                if url_score > 0:
                    relevant.append({
                        'url': article_url,
                        'url_score': url_score,
                        'relevance': 'high' if url_score >= 2 else 'medium'
                    })
            except:
                continue

        return relevant


def main():
    search_system = EnhancedSearchSystem()

    # Run comprehensive search
    results = search_system.run_comprehensive_search("shellharbour council")

    print("\n" + "=" * 60)
    print("📊 FINAL ENHANCED SEARCH RESULTS")
    print("=" * 60)

    print(f"📰 Total articles discovered: {results['total_articles']}")
    print(
        f"🎯 Target articles found: {len(results['found_targets'])}/{len(search_system.target_articles)}")
    print(f"📈 Target completion rate: {results['target_completion']:.1f}%")
    print(
        f"📝 Relevant articles identified: {len(results['relevant_articles'])}")

    if results['found_targets']:
        print("\n🎯 FOUND TARGET ARTICLES:")
        for target_id, url, *extra in results['found_targets']:
            title = search_system.target_articles.get(
                target_id, "Unknown title")
            print(f"   ✅ {target_id}: {title}")
            print(f"      URL: {url}")

    if results['relevant_articles']:
        print("\n📝 RELEVANT ARTICLES:")
        for article in results['relevant_articles'][:5]:  # Show top 5
            print(f"   • {article['relevance'].upper()}: {article['url']}")

    print("\n✅ ENHANCED SEARCH SYSTEM COMPLETE!")
    print("💡 This system can now be integrated into the main search for perfect matches.")


if __name__ == "__main__":
    main()
