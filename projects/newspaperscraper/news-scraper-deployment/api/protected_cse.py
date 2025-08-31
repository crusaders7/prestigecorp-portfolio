#!/usr/bin/env python3
"""
Google Custom Search API with Usage Protection
Prevents unexpected costs through multiple protection layers
"""

import json
import time
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from urllib.parse import urlencode

class APIUsageTracker:
    """Track and limit API usage to prevent unexpected costs"""
    
    def __init__(self, usage_file: str = "api_usage.json"):
        self.usage_file = usage_file
        self.daily_limit = 100  # Free tier: 100 queries/day
        self.hourly_limit = 20  # Rate limiting: 20 queries/hour
        self.cache_duration = 3600  # Cache results for 1 hour
        self.usage_data = self.load_usage_data()
    
    def load_usage_data(self) -> Dict:
        """Load usage tracking data"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "daily_count": 0,
            "hourly_count": 0,
            "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
            "last_reset_hour": datetime.now().strftime("%Y-%m-%d-%H"),
            "total_queries": 0,
            "cache": {}
        }
    
    def save_usage_data(self):
        """Save usage tracking data"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save usage data: {e}")
    
    def reset_counters_if_needed(self):
        """Reset daily and hourly counters if needed"""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_hour = now.strftime("%Y-%m-%d-%H")
        
        # Reset daily counter
        if self.usage_data["last_reset_date"] != current_date:
            self.usage_data["daily_count"] = 0
            self.usage_data["last_reset_date"] = current_date
            print(f"🔄 Daily API counter reset for {current_date}")
        
        # Reset hourly counter
        if self.usage_data["last_reset_hour"] != current_hour:
            self.usage_data["hourly_count"] = 0
            self.usage_data["last_reset_hour"] = current_hour
            print(f"🔄 Hourly API counter reset for {current_hour}")
    
    def can_make_request(self) -> tuple[bool, str]:
        """Check if we can make an API request"""
        self.reset_counters_if_needed()
        
        if self.usage_data["daily_count"] >= self.daily_limit:
            return False, f"Daily limit reached ({self.daily_limit} queries/day)"
        
        if self.usage_data["hourly_count"] >= self.hourly_limit:
            return False, f"Hourly rate limit reached ({self.hourly_limit} queries/hour)"
        
        return True, "OK"
    
    def get_cache_key(self, query: str, num: int = 10) -> str:
        """Generate cache key for query"""
        cache_string = f"{query.lower()}:{num}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_result(self, query: str, num: int = 10) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        cache_key = self.get_cache_key(query, num)
        
        if cache_key in self.usage_data["cache"]:
            cached = self.usage_data["cache"][cache_key]
            cache_time = datetime.fromisoformat(cached["timestamp"])
            
            if datetime.now() - cache_time < timedelta(seconds=self.cache_duration):
                print(f"📋 Using cached result for '{query}' (saved API call)")
                return cached["result"]
            else:
                # Remove expired cache
                del self.usage_data["cache"][cache_key]
        
        return None
    
    def cache_result(self, query: str, result: Dict, num: int = 10):
        """Cache API result"""
        cache_key = self.get_cache_key(query, num)
        self.usage_data["cache"][cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "query": query
        }
        
        # Clean old cache entries (keep last 50)
        if len(self.usage_data["cache"]) > 50:
            oldest_keys = sorted(
                self.usage_data["cache"].keys(),
                key=lambda k: self.usage_data["cache"][k]["timestamp"]
            )[:10]
            for key in oldest_keys:
                del self.usage_data["cache"][key]
    
    def record_api_call(self):
        """Record that an API call was made"""
        self.usage_data["daily_count"] += 1
        self.usage_data["hourly_count"] += 1
        self.usage_data["total_queries"] += 1
        self.save_usage_data()
        
        remaining_daily = self.daily_limit - self.usage_data["daily_count"]
        remaining_hourly = self.hourly_limit - self.usage_data["hourly_count"]
        
        print(f"📊 API Usage: Daily {self.usage_data['daily_count']}/{self.daily_limit}, "
              f"Hourly {self.usage_data['hourly_count']}/{self.hourly_limit}")
        
        if remaining_daily <= 10:
            print(f"⚠️  WARNING: Only {remaining_daily} daily API calls remaining!")
        if remaining_hourly <= 5:
            print(f"⚠️  WARNING: Only {remaining_hourly} hourly API calls remaining!")
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        self.reset_counters_if_needed()
        return {
            "daily_used": self.usage_data["daily_count"],
            "daily_limit": self.daily_limit,
            "daily_remaining": self.daily_limit - self.usage_data["daily_count"],
            "hourly_used": self.usage_data["hourly_count"],
            "hourly_limit": self.hourly_limit,
            "hourly_remaining": self.hourly_limit - self.usage_data["hourly_count"],
            "total_queries": self.usage_data["total_queries"],
            "cached_results": len(self.usage_data["cache"])
        }

class ProtectedGoogleCSE:
    """Google Custom Search with comprehensive cost protection"""
    
    def __init__(self, api_key: str = None):
        # API configuration
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"
        self.api_key = api_key or "AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0"
        
        # Initialize usage tracker
        self.tracker = APIUsageTracker()
        
        # Cost information
        self.cost_per_query = 0.005  # $5 per 1000 queries
        
        print("🛡️  API Protection Active")
        self.show_protection_status()
    
    def show_protection_status(self):
        """Display current protection status"""
        stats = self.tracker.get_usage_stats()
        estimated_cost = stats["total_queries"] * self.cost_per_query
        
        print("=" * 60)
        print("🛡️  API PROTECTION STATUS")
        print("=" * 60)
        print(f"Daily Usage: {stats['daily_used']}/{stats['daily_limit']} "
              f"({stats['daily_remaining']} remaining)")
        print(f"Hourly Usage: {stats['hourly_used']}/{stats['hourly_limit']} "
              f"({stats['hourly_remaining']} remaining)")
        print(f"Total Queries: {stats['total_queries']}")
        print(f"Cached Results: {stats['cached_results']}")
        print(f"Estimated Cost: ${estimated_cost:.3f}")
        print("=" * 60)
    
    def search_protected(self, query: str, num: int = 10) -> Dict:
        """Protected search with all safeguards"""
        
        # Step 1: Check cache first
        cached_result = self.tracker.get_cached_result(query, num)
        if cached_result:
            return cached_result
        
        # Step 2: Check if we can make API request
        can_request, reason = self.tracker.can_make_request()
        if not can_request:
            return {
                "success": False,
                "error": f"API request blocked: {reason}",
                "protection": "Rate limiting active",
                "suggestion": "Try again later or use cached results"
            }
        
        # Step 3: Validate input
        if not query or len(query.strip()) < 2:
            return {
                "success": False,
                "error": "Query too short (minimum 2 characters)",
                "protection": "Input validation"
            }
        
        if num > 10:
            print("⚠️  Limiting results to 10 to reduce costs")
            num = 10
        
        # Step 4: Make the API request
        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query.strip(),
                'num': num,
                'safe': 'off',
                'fields': 'items(title,link,snippet,displayLink),searchInformation(totalResults,searchTime)'
            }
            
            print(f"🔍 Making protected API call for: '{query}'")
            response = requests.get(self.api_endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                # Record successful API call
                self.tracker.record_api_call()
                
                data = response.json()
                result = {
                    "success": True,
                    "query": query,
                    "total_results": data.get('searchInformation', {}).get('totalResults', '0'),
                    "search_time": data.get('searchInformation', {}).get('searchTime', '0'),
                    "items": data.get('items', []),
                    "cost_info": {
                        "cost_per_query": self.cost_per_query,
                        "estimated_cost": self.cost_per_query
                    }
                }
                
                # Cache the result
                self.tracker.cache_result(query, result, num)
                
                return result
            
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}",
                    "response": response.text,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "exception": str(e)
            }
    
    def search_simple(self, query: str, max_results: int = 10) -> List[Dict]:
        """Simple search interface with protection"""
        result = self.search_protected(query, max_results)
        
        if result.get('success'):
            articles = []
            for item in result.get('items', []):
                articles.append({
                    'title': item.get('title', 'No title'),
                    'url': item.get('link', 'No URL'),
                    'snippet': item.get('snippet', 'No snippet'),
                    'domain': item.get('displayLink', 'Unknown domain')
                })
            return articles
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            return []
    
    def emergency_stop(self):
        """Emergency stop - block all API calls"""
        self.tracker.daily_limit = 0
        self.tracker.hourly_limit = 0
        self.tracker.save_usage_data()
        print("🚨 EMERGENCY STOP: All API calls blocked!")
    
    def reset_limits(self):
        """Reset usage limits (use with caution)"""
        self.tracker.usage_data["daily_count"] = 0
        self.tracker.usage_data["hourly_count"] = 0
        self.tracker.save_usage_data()
        print("🔄 Usage limits reset")

def main():
    """Main function with protected search"""
    import sys
    
    print("🛡️  Protected Google Custom Search Engine")
    print("Multiple layers of cost protection active")
    print("=" * 70)
    
    # Create protected CSE manager
    cse = ProtectedGoogleCSE()
    
    # Check if search query provided
    if len(sys.argv) > 1:
        query = sys.argv[1]
        
        # Special commands
        if query.lower() == "--stats":
            cse.show_protection_status()
            return
        elif query.lower() == "--emergency-stop":
            cse.emergency_stop()
            return
        elif query.lower() == "--reset":
            cse.reset_limits()
            return
        
        print(f"🔍 Protected search for: '{query}'")
        print("-" * 50)
        
        # Perform protected search
        articles = cse.search_simple(query, max_results=10)
        
        if articles:
            print(f"✅ Found {len(articles)} articles:")
            print()
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title']}")
                print(f"     🔗 {article['url']}")
                print(f"     📄 {article['snippet'][:100]}...")
                print()
        else:
            print("❌ No articles found or API limit reached")
        
        # Show updated protection status
        print("-" * 50)
        cse.show_protection_status()
        
    else:
        cse.show_protection_status()
        print("\n💡 Usage:")
        print("   python protected_cse.py 'your search query'")
        print("   python protected_cse.py --stats")
        print("   python protected_cse.py --emergency-stop")
        print("   python protected_cse.py --reset")

if __name__ == "__main__":
    main()
