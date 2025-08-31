#!/usr/bin/env python3
"""
Direct test of the comprehensive enhanced search system with 69 discovered categories
Tests the optimized tiered approach for perfect matches and performance
"""

import sys
import os
import json
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Add the api directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our search handler
from search import handler

def test_comprehensive_search_direct():
    """Test the comprehensive search directly without HTTP server"""
    
    # Test queries targeting different content types
    test_queries = [
        {
            "query": "Shellharbour Council", 
            "description": "Direct council search - should find perfect matches"
        },
        {
            "query": "council meeting", 
            "description": "Council governance - local government focus"
        },
        {
            "query": "development application", 
            "description": "Planning and development - council business"
        }
    ]
    
    print("🚀 COMPREHENSIVE SEARCH TESTING (Direct)")
    print("=" * 60)
    print(f"📊 Testing enhanced search with 69 discovered categories")
    print(f"🎯 Organized in 3 performance-optimized tiers")
    print("=" * 60)
    
    # Create handler instance  
    search_handler = handler(None, None, None)
    
    total_start_time = time.time()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 TEST {i}: {test_case['description']}")
        print(f"🔍 Query: '{test_case['query']}'")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # Test Strategy 2 (Category Scraping) with comprehensive categories
            results = search_handler.mercury_strategy2_comprehensive_categories(
                test_case['query'], 
                max_results=15
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ SUCCESS - {duration:.1f}s")
            print(f"📰 Found {len(results)} articles")
            
            # Show first few results for quality assessment
            for j, article in enumerate(results[:5], 1):
                title = article.get('title', 'No title')[:80]
                score = article.get('score', 0)
                print(f"   {j}. {title}... (Score: {score:.1f})")
            
            # Performance and relevance analysis
            if results:
                avg_score = sum(article.get('score', 0) for article in results) / len(results)
                high_relevance = sum(1 for article in results if article.get('score', 0) >= 8.0)
                perfect_matches = sum(1 for article in results if article.get('score', 0) >= 9.0)
                
                print(f"📊 Quality Metrics:")
                print(f"   • Average relevance score: {avg_score:.1f}/10")
                print(f"   • High relevance (8.0+): {high_relevance} articles")
                print(f"   • Perfect matches (9.0+): {perfect_matches} articles")
                print(f"   • Search time: {duration:.1f} seconds")
            else:
                print(f"📊 No results found")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    total_time = time.time() - total_start_time
    print("\n" + "=" * 60)
    print(f"🏁 COMPREHENSIVE TESTING COMPLETE")
    print(f"⏱️  Total testing time: {total_time:.1f} seconds")
    print(f"🎯 Enhanced with 69 categories across 3 optimized tiers")
    print(f"💡 Performance-optimized for perfect matches")
    print("=" * 60)

if __name__ == "__main__":
    test_comprehensive_search_direct()
