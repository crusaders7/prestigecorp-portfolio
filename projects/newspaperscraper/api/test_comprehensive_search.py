#!/usr/bin/env python3
"""
Test the comprehensive enhanced search system with 69 discovered categories
Tests the tiered approach for perfect matches and performance optimization
"""

import requests
import json
import time

def test_comprehensive_search():
    """Test the comprehensive search with all 69 discovered categories"""
    
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
        },
        {
            "query": "community event", 
            "description": "Local community activities"
        },
        {
            "query": "local business", 
            "description": "Economic and business news"
        }
    ]
    
    url = "http://localhost:8000/api/search"
    
    print("🚀 COMPREHENSIVE SEARCH TESTING")
    print("=" * 60)
    print(f"📊 Testing enhanced search with 69 discovered categories")
    print(f"🎯 Organized in 3 performance-optimized tiers")
    print("=" * 60)
    
    total_start_time = time.time()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 TEST {i}: {test_case['description']}")
        print(f"🔍 Query: '{test_case['query']}'")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            response = requests.post(url, json={
                'query': test_case['query'],
                'max_results': 15,
                'sources': ['mercury']
            }, timeout=300)  # Extended timeout for comprehensive search
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS - {duration:.1f}s")
                print(f"📰 Found {len(data['results'])} articles")
                
                # Show first few results for quality assessment
                for j, article in enumerate(data['results'][:5], 1):
                    title = article.get('title', 'No title')[:80]
                    score = article.get('score', 0)
                    print(f"   {j}. {title}... (Score: {score:.1f})")
                
                # Performance and relevance analysis
                avg_score = sum(article.get('score', 0) for article in data['results']) / len(data['results']) if data['results'] else 0
                high_relevance = sum(1 for article in data['results'] if article.get('score', 0) >= 8.0)
                perfect_matches = sum(1 for article in data['results'] if article.get('score', 0) >= 9.0)
                
                print(f"📊 Quality Metrics:")
                print(f"   • Average relevance score: {avg_score:.1f}/10")
                print(f"   • High relevance (8.0+): {high_relevance} articles")
                print(f"   • Perfect matches (9.0+): {perfect_matches} articles")
                print(f"   • Search time: {duration:.1f} seconds")
                
            else:
                print(f"❌ FAILED - Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT after 5 minutes")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    total_time = time.time() - total_start_time
    print("\n" + "=" * 60)
    print(f"🏁 COMPREHENSIVE TESTING COMPLETE")
    print(f"⏱️  Total testing time: {total_time:.1f} seconds")
    print(f"🎯 Enhanced with 69 categories across 3 optimized tiers")
    print(f"💡 Performance-optimized for perfect matches")
    print("=" * 60)

if __name__ == "__main__":
    test_comprehensive_search()
