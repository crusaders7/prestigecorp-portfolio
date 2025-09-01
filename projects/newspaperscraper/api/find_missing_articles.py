#!/usr/bin/env python3
"""
Search for specific missing Shellharbour articles by story ID patterns and content analysis
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re


def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'


class MissingArticleFinder:
    def __init__(self):
        self.base_url = "https://www.illawarramercury.com.au"
        self.headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }

        # Target articles we're looking for
        self.target_articles = [
            {
                'id': '9050660',
                'url': 'https://www.illawarramercury.com.au/story/9050660/shellharbour-council-plans-to-upgrade-jock-brown-oval/',
                'keywords': ['shellharbour', 'council', 'jock brown oval', 'upgrade'],
                'category_hints': ['sport', 'local-news', 'council']
            },
            {
                'id': '9046630',
                'url': 'https://www.illawarramercury.com.au/story/9046630/shellharbour-mayor-chris-homer-meets-with-sacked-ceo-mike-archer/',
                'keywords': ['shellharbour', 'mayor', 'chris homer', 'ceo', 'mike archer'],
                'category_hints': ['politics', 'local-news', 'council']
            },
            {
                'id': '9045329',
                'url': 'https://www.illawarramercury.com.au/story/9045329/wettest-august-hits-illawarra-junior-sports/',
                'keywords': ['august', 'illawarra', 'junior sports', 'wettest'],
                'category_hints': ['sport', 'junior-sport', 'weather']
            },
            {
                'id': '636609',
                'url': 'https://www.illawarramercury.com.au/story/636609/shellharbour-alp-candidate-tim-banfield-quits-and-backs-an-independent/',
                'keywords': ['shellharbour', 'alp', 'tim banfield', 'candidate', 'independent'],
                'category_hints': ['politics', 'local-news']
            },
            {
                'id': '9044604',
                'url': 'https://www.illawarramercury.com.au/story/9044604/shellharbour-council-culture-top-notch-says-mayor-chris-homer/',
                'keywords': ['shellharbour', 'council', 'culture', 'mayor', 'chris homer'],
                'category_hints': ['politics', 'local-news', 'council']
            }
        ]

    def test_direct_urls(self):
        """Test if we can access the articles directly"""
        print("🔍 TESTING DIRECT URL ACCESS")
        print("=" * 60)

        accessible_articles = []

        for article in self.target_articles:
            try:
                response = requests.get(
                    article['url'], headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    title_elem = soup.find('h1')
                    title = title_elem.get_text().strip() if title_elem else "No title found"

                    accessible_articles.append({
                        'id': article['id'],
                        'url': article['url'],
                        'title': title,
                        'accessible': True
                    })
                    print(f"✅ {article['id']}: {title}")
                else:
                    print(f"❌ {article['id']}: Status {response.status_code}")

            except Exception as e:
                print(f"❌ {article['id']}: Error - {e}")

        return accessible_articles

    def search_by_story_id_patterns(self):
        """Search for articles by looking for story ID patterns in category pages"""
        print(f"\n🔍 SEARCHING BY STORY ID PATTERNS")
        print("=" * 60)

        # Focus on categories most likely to contain these articles
        priority_categories = [
            "https://www.illawarramercury.com.au/news/local-news/",
            "https://www.illawarramercury.com.au/news/politics/",
            "https://www.illawarramercury.com.au/sport/local-sport/",
            "https://www.illawarramercury.com.au/sport/junior-sport/",
            "https://www.illawarramercury.com.au/community/",
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/"  # homepage
        ]

        found_articles = []
        target_ids = [article['id'] for article in self.target_articles]

        for category_url in priority_categories:
            print(
                f"\n📂 Searching {category_url.split('/')[-2] or 'homepage'}...")

            try:
                response = requests.get(
                    category_url, headers=self.headers, timeout=12)
                if response.status_code != 200:
                    print(f"   ❌ Status {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'lxml')
                category_articles = []

                # Find all story links and extract IDs
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/story/' in href:
                        # Extract story ID from URL
                        story_match = re.search(r'/story/(\d+)/', href)
                        if story_match:
                            story_id = story_match.group(1)
                            full_url = urljoin(self.base_url, href)

                            category_articles.append({
                                'id': story_id,
                                'url': full_url,
                                'href': href
                            })

                            # Check if this is one of our target articles
                            if story_id in target_ids:
                                # Get the title by following the link
                                try:
                                    article_response = requests.get(
                                        full_url, headers=self.headers, timeout=8)
                                    if article_response.status_code == 200:
                                        article_soup = BeautifulSoup(
                                            article_response.content, 'lxml')
                                        title_elem = article_soup.find('h1')
                                        title = title_elem.get_text().strip() if title_elem else "No title"

                                        found_articles.append({
                                            'id': story_id,
                                            'url': full_url,
                                            'title': title,
                                            'found_in': category_url
                                        })
                                        print(
                                            f"   🎯 FOUND TARGET: {story_id} - {title}")

                                except Exception:
                                    print(
                                        f"   🎯 FOUND ID: {story_id} - {full_url} (title unavailable)")

                print(
                    f"   📊 Found {len(category_articles)} total articles in category")

                # Look for articles with similar IDs (nearby chronologically)
                target_id_nums = [int(tid)
                                  for tid in target_ids if tid.isdigit()]
                nearby_articles = []

                for article in category_articles:
                    if article['id'].isdigit():
                        article_id_num = int(article['id'])
                        for target_num in target_id_nums:
                            # Check if article ID is within 100 of target (likely same time period)
                            if abs(article_id_num - target_num) <= 100:
                                nearby_articles.append(article)
                                break

                if nearby_articles:
                    print(
                        f"   📅 Found {len(nearby_articles)} articles with similar IDs (same time period)")

                time.sleep(0.5)  # Be respectful

            except Exception as e:
                print(f"   ❌ Error: {e}")

        return found_articles

    def search_by_keyword_combinations(self):
        """Search for articles using specific keyword combinations"""
        print(f"\n🔍 SEARCHING BY KEYWORD COMBINATIONS")
        print("=" * 60)

        search_queries = [
            "shellharbour council jock brown oval",
            "shellharbour mayor chris homer ceo",
            "illawarra junior sports august",
            "shellharbour tim banfield alp",
            "shellharbour council culture mayor"
        ]

        found_articles = []

        for query in search_queries:
            print(f"\n🔎 Searching for: '{query}'")

            # Try the site's search function
            try:
                search_url = f"{self.base_url}/search/?q={'+'.join(query.split())}"
                response = requests.get(
                    search_url, headers=self.headers, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')

                    # Look for search results
                    search_results = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/story/' in href:
                            search_results.append(urljoin(self.base_url, href))

                    print(
                        f"   📊 Site search found {len(search_results)} results")

                    # Check if any match our target articles
                    for result_url in search_results[:10]:  # Check top 10
                        story_match = re.search(r'/story/(\d+)/', result_url)
                        if story_match:
                            story_id = story_match.group(1)
                            target_ids = [article['id']
                                          for article in self.target_articles]
                            if story_id in target_ids:
                                print(
                                    f"   🎯 FOUND TARGET in search: {story_id}")
                                found_articles.append(result_url)

            except Exception as e:
                print(f"   ❌ Search error: {e}")

            time.sleep(1)

        return found_articles

    def analyze_article_distribution(self):
        """Analyze where these types of articles typically appear"""
        print(f"\n📊 ANALYZING ARTICLE DISTRIBUTION PATTERNS")
        print("=" * 60)

        # Check homepage for recent articles
        print("🏠 Analyzing homepage patterns...")
        try:
            response = requests.get(
                self.base_url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')

                homepage_articles = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/story/' in href:
                        story_match = re.search(r'/story/(\d+)/', href)
                        if story_match:
                            story_id = story_match.group(1)
                            homepage_articles.append(int(story_id))

                if homepage_articles:
                    homepage_articles.sort(reverse=True)  # Most recent first
                    print(
                        f"   📊 Homepage has {len(homepage_articles)} articles")
                    print(f"   📈 Most recent ID: {homepage_articles[0]}")
                    print(f"   📉 Oldest ID: {homepage_articles[-1]}")

                    # Check where our target articles fall in this range
                    target_ids = [
                        int(article['id']) for article in self.target_articles if article['id'].isdigit()]
                    for target_id in target_ids:
                        if target_id >= homepage_articles[-1] and target_id <= homepage_articles[0]:
                            print(
                                f"   🎯 Target {target_id} is in homepage range!")
                        else:
                            print(
                                f"   📅 Target {target_id} is outside homepage range")

        except Exception as e:
            print(f"   ❌ Homepage analysis error: {e}")

    def run_comprehensive_search(self):
        """Run all search methods"""
        print("🚀 COMPREHENSIVE MISSING ARTICLE SEARCH")
        print("=" * 70)

        # Test 1: Direct URL access
        accessible = self.test_direct_urls()

        # Test 2: Search by story ID patterns
        found_by_id = self.search_by_story_id_patterns()

        # Test 3: Search by keywords
        found_by_keywords = self.search_by_keyword_combinations()

        # Test 4: Analyze distribution patterns
        self.analyze_article_distribution()

        # Summary
        print(f"\n📋 SEARCH SUMMARY")
        print("=" * 60)
        print(f"🔗 Direct URL access: {len(accessible)} articles accessible")
        print(f"🆔 Found by ID pattern: {len(found_by_id)} articles")
        print(f"🔎 Found by keywords: {len(found_by_keywords)} articles")

        # Recommendations for improving search strategy
        print(f"\n💡 RECOMMENDATIONS FOR SEARCH IMPROVEMENT")
        print("=" * 60)

        if accessible:
            print(
                "✅ Articles are accessible - need to find which categories contain them")

            # Suggest categories that might contain these articles
            print("🎯 Suggested category additions:")
            suggested_categories = [
                "/news/council/",
                "/sport/facilities/",
                "/news/mayor/",
                "/politics/local/",
                "/sport/weather/",
                "/news/archive/",
                "/search/",  # Search results pages
                "/latest/",  # Latest news
                "/recent/",  # Recent articles
            ]

            for category in suggested_categories:
                test_url = self.base_url + category
                print(f"   • {test_url}")

        print(f"\n🔧 NEXT STEPS:")
        print("1. Add more specific categories for council/mayor news")
        print("2. Include archive/historical categories for older articles")
        print("3. Add pagination scanning for category pages")
        print("4. Implement date-based category exploration")
        print("5. Add search result page scraping")


if __name__ == "__main__":
    finder = MissingArticleFinder()
    finder.run_comprehensive_search()
