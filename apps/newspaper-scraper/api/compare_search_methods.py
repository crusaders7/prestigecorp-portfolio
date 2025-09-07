#!/usr/bin/env python3
"""
Comprehensive comparison test between original and optimized search
"""

import time
import json
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_search_method(search_func, method_name, query="shellharbour council", max_results=10):
    """Test a search method and return results with timing"""
    print(f"\n{'='*60}")
    print(f"🔍 Testing {method_name}")
    print(f"{'='*60}")

    start_time = time.time()
    try:
        results = search_func(query, max_results)
        end_time = time.time()

        duration = end_time - start_time
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Results: {len(results)} articles found")

        for i, url in enumerate(results[:5], 1):
            if isinstance(url, dict):
                title = url.get('title', 'No title')[:60]
                article_url = url.get('url', 'No URL')
                score = url.get('relevance_score', 'N/A')
                print(f"{i}. {title}...")
                print(f"   URL: {article_url}")
                print(f"   Score: {score}")
            else:
                print(f"{i}. {url}")

        return {
            'success': True,
            'duration': duration,
            'count': len(results),
            'results': results
        }

    except Exception as e:
        end_time = time.time()
        print(f"❌ Error: {e}")
        return {
            'success': False,
            'duration': end_time - start_time,
            'count': 0,
            'error': str(e)
        }


def create_test_handler_original():
    """Create a test handler for the original search method"""
    from search import handler as original_handler

    class TestHandler:
        def get_random_user_agent(self):
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        def search_illawarra_mercury(self, query, max_results):
            import types
            dummy = type('DummyHandler', (), {
                         'get_random_user_agent': self.get_random_user_agent})()
            search_method = types.MethodType(
                original_handler.search_illawarra_mercury, dummy)
            return search_method(query, max_results)

    return TestHandler()


def create_test_handler_optimized():
    """Create a test handler for the optimized search method"""
    from search_optimized import handler as optimized_handler

    class TestHandler:
        def get_random_user_agent(self):
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        def search_illawarra_mercury_optimized(self, query, max_results):
            import types
            dummy = type('DummyHandler', (), {
                         'get_random_user_agent': self.get_random_user_agent})()
            search_method = types.MethodType(
                optimized_handler.search_illawarra_mercury_optimized, dummy)
            return search_method(query, max_results)

    return TestHandler()


def main():
    """Run comprehensive comparison test"""
    print("🧪 COMPREHENSIVE SEARCH COMPARISON TEST")
    print("Testing both original and optimized search methods")

    query = "shellharbour council"
    max_results = 10

    # Test original search
    try:
        original_handler = create_test_handler_original()
        original_results = test_search_method(
            original_handler.search_illawarra_mercury,
            "ORIGINAL SEARCH (Sequential Strategies)",
            query,
            max_results
        )
    except Exception as e:
        print(f"❌ Failed to test original search: {e}")
        original_results = {'success': False, 'error': str(e)}

    # Test optimized search
    try:
        optimized_handler = create_test_handler_optimized()
        optimized_results = test_search_method(
            optimized_handler.search_illawarra_mercury_optimized,
            "OPTIMIZED SEARCH (Strategy 2 Priority)",
            query,
            max_results
        )
    except Exception as e:
        print(f"❌ Failed to test optimized search: {e}")
        optimized_results = {'success': False, 'error': str(e)}

    # Summary comparison
    print(f"\n{'='*60}")
    print("📊 PERFORMANCE COMPARISON SUMMARY")
    print(f"{'='*60}")

    if original_results.get('success'):
        print(f"🔵 Original Search:")
        print(f"   ⏱️  Time: {original_results['duration']:.2f} seconds")
        print(f"   📊 Results: {original_results['count']} articles")
    else:
        print(
            f"🔵 Original Search: ❌ Failed - {original_results.get('error', 'Unknown error')}")

    if optimized_results.get('success'):
        print(f"🟢 Optimized Search:")
        print(f"   ⏱️  Time: {optimized_results['duration']:.2f} seconds")
        print(f"   📊 Results: {optimized_results['count']} articles")
    else:
        print(
            f"🟢 Optimized Search: ❌ Failed - {optimized_results.get('error', 'Unknown error')}")

    # Performance improvement analysis
    if original_results.get('success') and optimized_results.get('success'):
        time_improvement = original_results['duration'] - \
            optimized_results['duration']
        time_improvement_pct = (
            time_improvement / original_results['duration']) * 100

        result_improvement = optimized_results['count'] - \
            original_results['count']

        print(f"\n🎯 OPTIMIZATION RESULTS:")
        print(
            f"   ⚡ Time improvement: {time_improvement:.2f}s ({time_improvement_pct:+.1f}%)")
        print(f"   📈 Result difference: {result_improvement:+d} articles")

        if time_improvement > 0 and result_improvement >= 0:
            print(f"   ✅ Optimization successful: Faster and same/better results!")
        elif time_improvement > 0:
            print(f"   ⚠️  Optimization trade-off: Faster but fewer results")
        elif result_improvement > 0:
            print(f"   ⚠️  Optimization trade-off: More results but slower")
        else:
            print(f"   ❌ Optimization needs improvement")

    print(f"\n✅ Comparison test completed!")


if __name__ == "__main__":
    main()
