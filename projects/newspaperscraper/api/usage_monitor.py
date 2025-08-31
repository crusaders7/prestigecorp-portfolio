#!/usr/bin/env python3
"""
Google CSE API Usage Monitor
Track costs and usage patterns
"""

import json
import os
from datetime import datetime
from protected_cse import APIUsageTracker

def show_detailed_stats():
    """Show detailed usage statistics"""
    tracker = APIUsageTracker()
    stats = tracker.get_usage_stats()
    
    print("🛡️  Google CSE API Usage Dashboard")
    print("=" * 60)
    
    # Current usage
    print("📊 Current Usage:")
    print(f"   Daily: {stats['daily_used']}/{stats['daily_limit']} "
          f"({stats['daily_remaining']} remaining)")
    print(f"   Hourly: {stats['hourly_used']}/{stats['hourly_limit']} "
          f"({stats['hourly_remaining']} remaining)")
    
    # Cost tracking
    estimated_cost = stats['total_queries'] * 0.005
    print(f"\n💰 Cost Tracking:")
    print(f"   Total API Calls: {stats['total_queries']}")
    print(f"   Estimated Cost: ${estimated_cost:.3f}")
    print(f"   Cost per Query: $0.005")
    
    # Cache efficiency
    if stats['total_queries'] > 0:
        cache_hit_rate = (stats['cached_results'] / max(stats['total_queries'], 1)) * 100
        print(f"\n📋 Cache Performance:")
        print(f"   Cached Results: {stats['cached_results']}")
        print(f"   Cache Hit Rate: {cache_hit_rate:.1f}%")
        print(f"   Cost Saved: ${stats['cached_results'] * 0.005:.3f}")
    
    # Warnings
    print(f"\n⚠️  Status Alerts:")
    if stats['daily_remaining'] <= 10:
        print(f"   🚨 Low daily quota: {stats['daily_remaining']} calls left")
    if stats['hourly_remaining'] <= 2:
        print(f"   🚨 Low hourly quota: {stats['hourly_remaining']} calls left")
    if estimated_cost >= 0.20:
        print(f"   🚨 High cost alert: ${estimated_cost:.3f}")
    
    if stats['daily_remaining'] > 10 and stats['hourly_remaining'] > 2 and estimated_cost < 0.20:
        print("   ✅ All systems normal")
    
    print("=" * 60)

def reset_daily_usage():
    """Reset daily usage counter (emergency use only)"""
    tracker = APIUsageTracker()
    tracker.usage_data["daily_count"] = 0
    tracker.save_usage_data()
    print("🔄 Daily usage counter reset")

def emergency_stop():
    """Immediately stop all API usage"""
    tracker = APIUsageTracker()
    tracker.daily_limit = 0
    tracker.hourly_limit = 0
    tracker.save_usage_data()
    print("🚨 EMERGENCY STOP ACTIVATED")
    print("   All API calls are now blocked")
    print("   Edit api_usage.json to restore limits")

def show_cache_contents():
    """Show cached search results"""
    tracker = APIUsageTracker()
    cache = tracker.usage_data.get("cache", {})
    
    print("📋 Cached Search Results:")
    print("=" * 60)
    
    if not cache:
        print("   No cached results found")
        return
    
    for cache_key, cached_data in cache.items():
        query = cached_data.get("query", "Unknown")
        timestamp = cached_data.get("timestamp", "Unknown")
        result_count = len(cached_data.get("result", {}).get("items", []))
        
        print(f"   Query: '{query}'")
        print(f"   Cached: {timestamp}")
        print(f"   Results: {result_count}")
        print("   " + "-" * 50)

def main():
    """Main monitoring interface"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "--detailed":
            show_detailed_stats()
        elif command == "--cache":
            show_cache_contents()
        elif command == "--reset":
            reset_daily_usage()
        elif command == "--emergency":
            emergency_stop()
        else:
            print("Available commands:")
            print("  --detailed    Show detailed statistics")
            print("  --cache       Show cached results")
            print("  --reset       Reset daily counter")
            print("  --emergency   Emergency stop all API calls")
    else:
        show_detailed_stats()

if __name__ == "__main__":
    main()
