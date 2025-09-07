#!/usr/bin/env python3
"""
Analyze URL structure and numbering system for Illawarra Mercury articles
Investigate what the numbers after /story/ represent
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import json


def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'


class URLStructureAnalyzer:
    def __init__(self):
        self.base_url = "https://www.illawarramercury.com.au"
        self.headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.analyzed_urls = []

    def analyze_target_url(self, target_url):
        """Analyze the specific target URL that was missed"""
        print("🎯 ANALYZING TARGET URL")
        print("=" * 60)
        print(f"Target: {target_url}")

        try:
            response = requests.get(
                target_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')

                # Extract article metadata
                title = soup.find('h1')
                title_text = title.get_text().strip() if title else "No title"

                # Look for publication date
                pub_date = None
                date_patterns = [
                    soup.find('time'),
                    soup.find(attrs={'class': re.compile(
                        r'date|time|publish', re.I)}),
                    soup.find(attrs={'id': re.compile(
                        r'date|time|publish', re.I)}),
                ]

                for date_elem in date_patterns:
                    if date_elem:
                        pub_date = date_elem.get(
                            'datetime') or date_elem.get_text()
                        if pub_date:
                            break

                # Extract URL components
                url_parts = target_url.split('/')
                story_id = None
                for i, part in enumerate(url_parts):
                    if part == 'story' and i + 1 < len(url_parts):
                        story_id = url_parts[i + 1]
                        break

                print(f"📰 Title: {title_text}")
                print(f"🆔 Story ID: {story_id}")
                print(f"📅 Publication Date: {pub_date}")
                print(f"✅ Status: Accessible")

                # Try to decode the story ID
                if story_id:
                    self.analyze_story_id(story_id, pub_date)

                return {
                    'title': title_text,
                    'story_id': story_id,
                    'pub_date': pub_date,
                    'accessible': True
                }

            else:
                print(f"❌ Status: {response.status_code}")
                return {'accessible': False, 'status': response.status_code}

        except Exception as e:
            print(f"❌ Error accessing target URL: {e}")
            return {'accessible': False, 'error': str(e)}

    def analyze_story_id(self, story_id, pub_date):
        """Analyze what the story ID number could represent"""
        print(f"\n🔍 STORY ID ANALYSIS")
        print("-" * 40)

        # Check if it's a timestamp
        try:
            # Unix timestamp (seconds)
            if len(story_id) == 10:
                timestamp = datetime.fromtimestamp(int(story_id))
                print(f"Unix timestamp (seconds): {timestamp}")

            # Unix timestamp (milliseconds)
            elif len(story_id) == 13:
                timestamp = datetime.fromtimestamp(int(story_id) / 1000)
                print(f"Unix timestamp (milliseconds): {timestamp}")

            # Other timestamp formats
            else:
                print(f"ID length: {len(story_id)} digits")

                # Try interpreting as date components
                if len(story_id) >= 8:
                    # YYYYMMDD format
                    year_part = story_id[:4]
                    month_part = story_id[4:6] if len(story_id) > 4 else ""
                    day_part = story_id[6:8] if len(story_id) > 6 else ""

                    if year_part.isdigit() and int(year_part) > 2000 and int(year_part) < 2030:
                        print(
                            f"Possible date components: {year_part}-{month_part}-{day_part}")

                # Check if it's sequential
                print(f"Raw number: {story_id}")

        except ValueError:
            print(f"Not a valid timestamp: {story_id}")

        # Compare with publication date if available
        if pub_date:
            print(f"Published: {pub_date}")

    def find_similar_articles(self, target_id):
        """Find articles with similar IDs to understand the pattern"""
        print(f"\n🔍 SEARCHING FOR SIMILAR ARTICLE IDS")
        print("=" * 60)

        target_num = int(target_id)
        search_ranges = [
            range(target_num - 50, target_num + 50),  # Close range
            range(target_num - 500, target_num + 500, 10),  # Medium range
        ]

        found_articles = []

        for search_range in search_ranges:
            print(f"Searching range around {target_id}...")

            for test_id in search_range:
                if len(found_articles) >= 20:  # Limit to avoid too many requests
                    break

                test_url = f"{self.base_url}/story/{test_id}/"

                try:
                    response = requests.get(
                        test_url, headers=self.headers, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'lxml')
                        title_elem = soup.find('h1')
                        title = title_elem.get_text().strip() if title_elem else "No title"

                        # Look for date
                        date_elem = soup.find('time')
                        article_date = date_elem.get(
                            'datetime') if date_elem else "No date"

                        found_articles.append({
                            'id': test_id,
                            'title': title,
                            'date': article_date,
                            'url': test_url
                        })

                        print(
                            f"  ✅ {test_id}: {title[:50]}... ({article_date})")

                except Exception:
                    continue

                time.sleep(0.1)  # Be respectful

            if found_articles:
                break  # Found some, no need to search wider

        return found_articles

    def analyze_id_patterns(self, articles):
        """Analyze patterns in the found article IDs"""
        if not articles:
            return

        print(f"\n📊 ID PATTERN ANALYSIS")
        print("=" * 40)

        # Sort by ID
        articles.sort(key=lambda x: x['id'])

        print("ID sequence analysis:")
        for i, article in enumerate(articles):
            if i > 0:
                gap = article['id'] - articles[i-1]['id']
                print(f"  {article['id']} (gap: +{gap}) - {article['date']}")
            else:
                print(f"  {article['id']} - {article['date']}")

        # Look for date correlation
        print(f"\nDate correlation analysis:")
        for article in articles:
            if article['date'] and article['date'] != "No date":
                try:
                    # Parse the date and see if there's a correlation
                    date_str = article['date']
                    print(f"  ID {article['id']}: {date_str}")
                except Exception:
                    continue

    def search_by_content_keywords(self, keywords):
        """Search for articles by content keywords to find missed articles"""
        print(f"\n🔍 SEARCHING BY CONTENT KEYWORDS")
        print("=" * 60)

        found_articles = []

        # Try direct site search first
        search_url = f"{self.base_url}/search/"

        for keyword in keywords:
            try:
                params = {'q': keyword}
                response = requests.get(
                    search_url, headers=self.headers, params=params, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')

                    # Look for article links
                    for link in soup.find_all('a', href=re.compile(r'/story/\d+')):
                        href = link['href']
                        title_elem = link.find(string=True)
                        title = title_elem.strip() if title_elem else "No title"

                        if 'shellharbour' in title.lower() or 'council' in title.lower():
                            full_url = href if href.startswith(
                                'http') else self.base_url + href
                            found_articles.append({
                                'url': full_url,
                                'title': title,
                                'keyword': keyword
                            })
                            print(f"  ✅ Found: {title}")
                            print(f"     URL: {full_url}")

            except Exception as e:
                print(f"  ❌ Search failed for '{keyword}': {e}")
                continue

            time.sleep(1)  # Be respectful

        return found_articles

    def generate_id_range_urls(self, center_id, range_size=1000):
        """Generate URLs for a range of story IDs around a center point"""
        print(f"\n🔢 GENERATING ID RANGE URLS")
        print("=" * 60)

        center_num = int(center_id)
        start_id = center_num - range_size // 2
        end_id = center_num + range_size // 2

        urls = []
        for story_id in range(start_id, end_id + 1):
            url = f"{self.base_url}/story/{story_id}/"
            urls.append(url)

        print(f"Generated {len(urls)} URLs from {start_id} to {end_id}")
        return urls

    def run_comprehensive_analysis(self, target_url):
        """Run complete analysis of the URL structure"""
        print("🚀 COMPREHENSIVE URL STRUCTURE ANALYSIS")
        print("=" * 70)

        # Step 1: Analyze the target URL
        target_analysis = self.analyze_target_url(target_url)

        if not target_analysis.get('accessible'):
            print("❌ Target URL not accessible, cannot proceed with analysis")
            return

        story_id = target_analysis.get('story_id')
        if not story_id:
            print("❌ Could not extract story ID from target URL")
            return

        # Step 2: Find similar articles
        similar_articles = self.find_similar_articles(story_id)

        # Step 3: Analyze patterns
        if similar_articles:
            self.analyze_id_patterns(similar_articles)

        # Step 4: Search by keywords
        keywords = ['shellharbour council',
                    'shellharbour mayor', 'council ceo']
        keyword_results = self.search_by_content_keywords(keywords)

        # Step 5: Generate recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("=" * 40)
        print("Based on analysis, to find more articles like the target:")
        print(f"1. Search ID range around {story_id} (±1000)")
        print("2. Use content-based search for specific keywords")
        print("3. Check if articles are in different categories not yet discovered")

        # Step 6: Generate URL ranges for testing
        id_range_urls = self.generate_id_range_urls(story_id, 200)

        # Save results
        results = {
            'target_analysis': target_analysis,
            'similar_articles': similar_articles,
            'keyword_results': keyword_results,
            'id_range_urls': id_range_urls[:50],  # First 50 for testing
            'recommendations': [
                f"Story ID pattern detected: {len(story_id)} digits",
                f"Consider scanning ID range {int(story_id) - 500} to {int(story_id) + 500}",
                "Articles may not appear in standard category listings",
                "Use direct ID enumeration for comprehensive coverage"
            ]
        }

        with open('url_structure_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"💾 Analysis saved to url_structure_analysis.json")
        return results


if __name__ == "__main__":
    target_url = "https://www.illawarramercury.com.au/story/9050857/push-for-all-councillors-to-select-new-ceo-knocked-back-by-shellharbour-mayor/"

    analyzer = URLStructureAnalyzer()
    analyzer.run_comprehensive_analysis(target_url)
