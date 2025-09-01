#!/usr/bin/env python3
"""
Test the enhanced category scraping
"""

import sys
import os
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_enhanced_categories():
    """Test the enhanced category discovery"""

    print("🧪 TESTING ENHANCED CATEGORY SCRAPING")
    print("=" * 60)

    try:
        # Import the updated search module
        from search import handler as search_handler

        # Create a test handler
        class TestHandler:
            def get_random_user_agent(self):
                return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

            def search_illawarra_mercury(self, query, max_results):
                import types
                dummy = type('DummyHandler', (), {
                             'get_random_user_agent': self.get_random_user_agent})()
                search_method = types.MethodType(
                    search_handler.search_illawarra_mercury, dummy)
                return search_method(query, max_results)

        handler = TestHandler()

        # Test with the enhanced categories
        print(f"🔍 Testing enhanced search for 'shellharbour council'...")
        start_time = time.time()

        results = handler.search_illawarra_mercury("shellharbour council", 10)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n📊 ENHANCED CATEGORY RESULTS:")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📰 Found: {len(results)} articles")

        print(f"\n🔗 Article URLs:")
        for i, url in enumerate(results[:10], 1):
            if 'shellharbour' in url.lower():
                print(f"{i}. ✅ {url}")
            else:
                print(f"{i}. ⚪ {url}")

        # Quick quality check
        shellharbour_count = sum(
            1 for url in results if 'shellharbour' in url.lower())
        council_count = sum(1 for url in results if 'council' in url.lower())

        print(f"\n🎯 RELEVANCE ANALYSIS:")
        print(
            f"📍 URLs with 'shellharbour': {shellharbour_count}/{len(results)} ({shellharbour_count/len(results)*100:.1f}%)")
        print(
            f"🏛️  URLs with 'council': {council_count}/{len(results)} ({council_count/len(results)*100:.1f}%)")

        if shellharbour_count > 0:
            print("✅ Enhanced categories successfully finding Shellharbour content!")
        else:
            print("⚠️  No Shellharbour-specific content found")

        return {
            'duration': duration,
            'total_results': len(results),
            'shellharbour_results': shellharbour_count,
            'council_results': council_count,
            'results': results
        }

    except Exception as e:
        print(f"❌ Error testing enhanced categories: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_category_coverage():
    """Test how many articles we can get from the enhanced categories"""

    print(f"\n🏗️  TESTING CATEGORY COVERAGE")
    print("=" * 60)

    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Test the enhanced category list
        enhanced_categories = [
            ("Homepage", "https://www.illawarramercury.com.au"),
            ("Sport", "https://www.illawarramercury.com.au/sport/"),
            ("Entertainment", "https://www.illawarramercury.com.au/entertainment/"),
            ("News", "https://www.illawarramercury.com.au/news/"),
            ("Lifestyle", "https://www.illawarramercury.com.au/lifestyle/"),
            ("Business", "https://www.illawarramercury.com.au/news/business/"),
            ("Environment", "https://www.illawarramercury.com.au/news/environment/"),
            ("Local News", "https://www.illawarramercury.com.au/news/local-news/"),
            ("Basketball", "https://www.illawarramercury.com.au/sport/basketball/"),
            ("Education", "https://www.illawarramercury.com.au/news/education/"),
            ("Health", "https://www.illawarramercury.com.au/news/health/"),
            ("Politics", "https://www.illawarramercury.com.au/news/politics/"),
            ("Cricket", "https://www.illawarramercury.com.au/sport/cricket/"),
            ("Community", "https://www.illawarramercury.com.au/community/")
        ]

        total_articles = 0
        working_categories = 0

        for name, url in enhanced_categories:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    story_links = soup.find_all(
                        'a', href=lambda x: x and '/story/' in x)
                    article_count = len(story_links)
                    total_articles += article_count
                    working_categories += 1
                    print(f"✅ {name:<15} {article_count:>3} articles")
                else:
                    print(f"❌ {name:<15} Status {response.status_code}")
            except Exception as e:
                print(f"❌ {name:<15} Error: {str(e)[:30]}...")

            time.sleep(0.3)

        print(f"\n📊 COVERAGE SUMMARY:")
        print(f"✅ Working categories: {working_categories}/14")
        print(f"📰 Total articles available: {total_articles}")
        print(
            f"📈 Average per category: {total_articles/working_categories:.1f}")

        return {
            'working_categories': working_categories,
            'total_articles': total_articles,
            'categories_tested': len(enhanced_categories)
        }

    except Exception as e:
        print(f"❌ Error testing coverage: {e}")
        return None


def main():
    """Run both tests"""

    # Test 1: Enhanced search functionality
    search_results = test_enhanced_categories()

    # Test 2: Category coverage
    coverage_results = test_category_coverage()

    # Summary
    print(f"\n🎯 ENHANCEMENT SUMMARY")
    print("=" * 60)

    if search_results:
        print(f"🔍 Search Performance:")
        print(f"   ⏱️  Duration: {search_results['duration']:.2f}s")
        print(f"   📰 Results: {search_results['total_results']}")
        print(
            f"   🎯 Relevance: {search_results['shellharbour_results']} Shellharbour matches")

    if coverage_results:
        print(f"📊 Category Coverage:")
        print(
            f"   ✅ Working: {coverage_results['working_categories']}/14 categories")
        print(
            f"   📰 Articles: {coverage_results['total_articles']} total available")

    print(f"\n✅ Enhanced category testing completed!")


if __name__ == "__main__":
    main()
