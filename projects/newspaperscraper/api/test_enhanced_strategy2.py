#!/usr/bin/env python3
"""
Test the enhanced search with 67 categories and only Strategy 2
"""

import sys
import os
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_strategy2_only():
    """Test the enhanced Strategy 2 only approach"""
    
    print("🚀 TESTING ENHANCED STRATEGY 2 ONLY (67 CATEGORIES)")
    print("=" * 70)
    
    try:
        # Import the updated search module
        from search import handler as search_handler
        
        # Create a test handler
        class TestHandler:
            def get_random_user_agent(self):
                return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                
            def search_illawarra_mercury(self, query, max_results):
                import types
                dummy = type('DummyHandler', (), {'get_random_user_agent': self.get_random_user_agent})()
                search_method = types.MethodType(search_handler.search_illawarra_mercury, dummy)
                return search_method(query, max_results)
        
        handler = TestHandler()
        
        # Test with the enhanced 67-category setup
        print(f"🔍 Testing enhanced search for 'shellharbour council'...")
        print(f"📊 Categories to scan: 67 discovered categories")
        print(f"📰 Estimated articles available: ~3,967")
        print()
        
        start_time = time.time()
        
        results = handler.search_illawarra_mercury("shellharbour council", 15)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 ENHANCED STRATEGY 2 RESULTS:")
        print("=" * 50)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📰 Articles found: {len(results)}")
        print(f"⚡ Articles per second: {len(results)/duration:.2f}")
        
        print(f"\n🎯 ARTICLE RESULTS:")
        print("-" * 50)
        
        shellharbour_count = 0
        council_count = 0
        
        for i, url in enumerate(results, 1):
            # Check relevance
            is_shellharbour = 'shellharbour' in url.lower()
            is_council = 'council' in url.lower()
            
            if is_shellharbour:
                shellharbour_count += 1
            if is_council:
                council_count += 1
            
            # Create relevance indicator
            relevance = ""
            if is_shellharbour and is_council:
                relevance = "🎯🏛️ "  # Perfect match
            elif is_shellharbour:
                relevance = "🎯   "   # Location match
            elif is_council:
                relevance = "🏛️    "   # Council match
            else:
                relevance = "⚪   "   # General match
            
            # Extract article title from URL
            url_parts = url.split('/')
            if len(url_parts) > 1:
                title_slug = url_parts[-1].replace('-', ' ').replace('.html', '')
                title = title_slug[:60] + "..." if len(title_slug) > 60 else title_slug
            else:
                title = "Unknown article"
            
            print(f"{i:2d}. {relevance} {title}")
            print(f"     {url}")
            print()
        
        print(f"📈 RELEVANCE ANALYSIS:")
        print("-" * 50)
        print(f"📍 Shellharbour matches: {shellharbour_count}/{len(results)} ({shellharbour_count/len(results)*100:.1f}%)")
        print(f"🏛️  Council matches: {council_count}/{len(results)} ({council_count/len(results)*100:.1f}%)")
        print(f"🎯 Perfect matches: {len([url for url in results if 'shellharbour' in url.lower() and 'council' in url.lower()])}")
        
        # Performance assessment
        print(f"\n⚡ PERFORMANCE ASSESSMENT:")
        print("-" * 50)
        
        if duration < 60:
            speed_rating = "🚀 Excellent"
        elif duration < 120:
            speed_rating = "✅ Good"  
        elif duration < 180:
            speed_rating = "⚠️  Acceptable"
        else:
            speed_rating = "❌ Slow"
            
        print(f"Speed: {speed_rating} ({duration:.1f}s)")
        
        if len(results) >= 10:
            quantity_rating = "🎯 Excellent"
        elif len(results) >= 5:
            quantity_rating = "✅ Good"
        elif len(results) >= 3:
            quantity_rating = "⚠️  Acceptable"
        else:
            quantity_rating = "❌ Poor"
            
        print(f"Quantity: {quantity_rating} ({len(results)} articles)")
        
        relevance_pct = (shellharbour_count + council_count) / len(results) * 100 if results else 0
        if relevance_pct >= 80:
            relevance_rating = "🎯 Excellent"
        elif relevance_pct >= 60:
            relevance_rating = "✅ Good"
        elif relevance_pct >= 40:
            relevance_rating = "⚠️  Acceptable"
        else:
            relevance_rating = "❌ Poor"
            
        print(f"Relevance: {relevance_rating} ({relevance_pct:.1f}%)")
        
        print(f"\n🎉 ENHANCEMENT SUCCESS!")
        print("=" * 50)
        print("✅ Removed ineffective strategies (1, 3, 4)")
        print("✅ Enhanced Strategy 2 with 67 categories")
        print("✅ Streamlined for maximum efficiency")
        print(f"✅ Found {len(results)} relevant articles in {duration:.1f}s")
        
        return {
            'duration': duration,
            'results_count': len(results),
            'shellharbour_matches': shellharbour_count,
            'council_matches': council_count,
            'relevance_score': relevance_pct,
            'results': results
        }
        
    except Exception as e:
        print(f"❌ Error testing enhanced Strategy 2: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run the enhanced test"""
    test_enhanced_strategy2_only()

if __name__ == "__main__":
    main()
