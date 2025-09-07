#!/usr/bin/env python3
"""
Enhanced Intelligent Article Finder with Google CSE Integration
Uses the discovered Google CSE configuration plus multiple fallback strategies

Key Features:
1. Uses extracted Google CSE ID (012527284968046999840:zzi3qgsoibq)
2. Multiple search strategies if CSE doesn't work
3. Intelligent URL construction and validation
4. Advanced result filtering and ranking
"""

import requests
import json
import re
import time
from urllib.parse import urlencode, quote, urlparse
from datetime import datetime, timedelta
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Optional
import random


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    confidence: float
    discovered_at: str


class EnhancedIntelligentFinder:
    def __init__(self):
        # Google CSE configuration discovered from website
        self.cse_id = "012527284968046999840:zzi3qgsoibq"
        self.engine_id = "012527284968046999840"

        # Initialize database for caching results
        self.db_path = "enhanced_search_cache.db"
        self._init_database()

        # Base URLs and patterns
        self.base_url = "https://www.illawarramercury.com.au"
        self.story_pattern = r"/story/([^/]+)/(\d+)/"

        # Search strategies ranking
        self.strategies = [
            "google_cse_direct",
            "google_site_search",
            "bing_site_search",
            "duckduckgo_site_search",
            "direct_site_search",
            "story_id_discovery"
        ]

    def _init_database(self):
        """Initialize SQLite database for caching search results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                snippet TEXT,
                source TEXT NOT NULL,
                confidence REAL NOT NULL,
                discovered_at TEXT NOT NULL,
                last_verified TEXT,
                is_accessible INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_query ON enhanced_search_results(query)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_confidence ON enhanced_search_results(confidence DESC)
        ''')

        conn.commit()
        conn.close()

    def search_comprehensive(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """
        Comprehensive search using all available strategies
        """
        print(f"🔍 Starting comprehensive search for: '{query}'")
        print("=" * 60)

        all_results = []
        strategy_results = {}

        # Try each search strategy
        for strategy in self.strategies:
            print(f"\n📡 Trying strategy: {strategy}")
            try:
                if strategy == "google_cse_direct":
                    results = self._google_cse_search(query)
                elif strategy == "google_site_search":
                    results = self._google_site_search(query)
                elif strategy == "bing_site_search":
                    results = self._bing_site_search(query)
                elif strategy == "duckduckgo_site_search":
                    results = self._duckduckgo_site_search(query)
                elif strategy == "direct_site_search":
                    results = self._direct_site_search(query)
                elif strategy == "story_id_discovery":
                    results = self._story_id_discovery(query)
                else:
                    results = []

                strategy_results[strategy] = results
                all_results.extend(results)
                print(f"✅ {strategy}: Found {len(results)} results")

                # Add delay between strategies to be respectful
                time.sleep(1)

            except Exception as e:
                print(f"❌ {strategy}: Error - {e}")
                strategy_results[strategy] = []

        # Remove duplicates and rank results
        unique_results = self._deduplicate_and_rank(all_results, query)

        # Cache results
        self._cache_results(query, unique_results)

        # Display summary
        print(f"\n📊 Search Summary for '{query}'")
        print("-" * 40)
        for strategy, results in strategy_results.items():
            print(f"{strategy}: {len(results)} results")
        print(f"Total unique results: {len(unique_results)}")

        return unique_results[:max_results]

    def _google_cse_search(self, query: str) -> List[SearchResult]:
        """Search using the discovered Google CSE configuration"""
        try:
            # Try the embedded CSE approach
            cse_url = "https://cse.google.com/cse/publicurl"
            params = {
                'cx': self.cse_id,
                'q': query,
                'ie': 'UTF-8',
                'num': 10
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.illawarramercury.com.au/'
            }

            response = requests.get(
                cse_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_cse_results(response.text, query, "Google CSE Direct")
            else:
                # Try alternative CSE approach
                return self._google_cse_alternative(query)

        except Exception as e:
            print(f"CSE search error: {e}")
            return []

    def _google_cse_alternative(self, query: str) -> List[SearchResult]:
        """Alternative approach to use Google CSE"""
        try:
            # Try to access the CSE through the website's search functionality
            search_url = f"{self.base_url}/search/"
            params = {
                'q': query,
                'cx': self.cse_id
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': f'{self.base_url}/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            response = requests.get(
                search_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_website_search_results(response.text, query, "Google CSE Alternative")

        except Exception as e:
            print(f"CSE alternative error: {e}")

        return []

    def _google_site_search(self, query: str) -> List[SearchResult]:
        """Search using Google with site: operator"""
        try:
            search_url = "https://www.google.com/search"
            site_query = f"site:illawarramercury.com.au {query}"

            params = {
                'q': site_query,
                'num': 10,
                'hl': 'en'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            response = requests.get(
                search_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_google_results(response.text, query, "Google Site Search")

        except Exception as e:
            print(f"Google search error: {e}")

        return []

    def _bing_site_search(self, query: str) -> List[SearchResult]:
        """Search using Bing with site: operator"""
        try:
            search_url = "https://www.bing.com/search"
            site_query = f"site:illawarramercury.com.au {query}"

            params = {
                'q': site_query,
                'count': 10
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            response = requests.get(
                search_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_bing_results(response.text, query, "Bing Site Search")

        except Exception as e:
            print(f"Bing search error: {e}")

        return []

    def _duckduckgo_site_search(self, query: str) -> List[SearchResult]:
        """Search using DuckDuckGo with site: operator"""
        try:
            search_url = "https://duckduckgo.com/html/"
            site_query = f"site:illawarramercury.com.au {query}"

            params = {
                'q': site_query
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            response = requests.get(
                search_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_duckduckgo_results(response.text, query, "DuckDuckGo Site Search")

        except Exception as e:
            print(f"DuckDuckGo search error: {e}")

        return []

    def _direct_site_search(self, query: str) -> List[SearchResult]:
        """Search directly on the website if it has a search API"""
        try:
            # Try to find the website's internal search API
            search_endpoints = [
                f"{self.base_url}/api/search/",
                f"{self.base_url}/search/api/",
                f"{self.base_url}/api/v1/search/",
                f"{self.base_url}/api/v2/search/"
            ]

            for endpoint in search_endpoints:
                try:
                    params = {'q': query, 'limit': 10}
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'application/json, text/html, */*',
                        'Referer': f'{self.base_url}/'
                    }

                    response = requests.get(
                        endpoint, params=params, headers=headers, timeout=10)

                    if response.status_code == 200:
                        # Try to parse as JSON first
                        try:
                            data = response.json()
                            return self._parse_api_results(data, query, "Direct Site API")
                        except:
                            # If not JSON, parse as HTML
                            return self._parse_website_search_results(response.text, query, "Direct Site Search")

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Direct site search error: {e}")

        return []

    def _story_id_discovery(self, query: str) -> List[SearchResult]:
        """Search by constructing potential story URLs based on query"""
        results = []

        try:
            # Generate potential story slugs from query
            query_words = re.sub(r'[^\w\s]', '', query.lower()).split()
            potential_slugs = [
                '-'.join(query_words),
                '-'.join(query_words[:3]),
                '-'.join(query_words[-3:]
                         ) if len(query_words) > 3 else '-'.join(query_words)
            ]

            # Generate potential story IDs around recent range
            # Based on our reverse engineering: current range 9003555 - 9053686
            current_max = 9053686
            search_range = range(current_max - 1000, current_max + 1)

            for slug in potential_slugs:
                for story_id in random.sample(list(search_range), min(50, len(search_range))):
                    url = f"{self.base_url}/story/{slug}/{story_id}/"

                    # Quick check if URL exists
                    try:
                        head_response = requests.head(url, timeout=5)
                        if head_response.status_code == 200:
                            # Get the actual page to extract title
                            page_response = requests.get(url, timeout=10)
                            if page_response.status_code == 200:
                                title = self._extract_title_from_html(
                                    page_response.text)
                                if title and any(word in title.lower() for word in query_words):
                                    results.append(SearchResult(
                                        title=title,
                                        url=url,
                                        snippet=f"Story discovered by ID pattern matching for: {query}",
                                        source="Story ID Discovery",
                                        confidence=0.8,
                                        discovered_at=datetime.now().isoformat()
                                    ))

                                    if len(results) >= 5:  # Limit to prevent too many requests
                                        break
                    except:
                        continue

                if len(results) >= 5:
                    break

        except Exception as e:
            print(f"Story ID discovery error: {e}")

        return results

    def _parse_cse_results(self, html: str, query: str, source: str) -> List[SearchResult]:
        """Parse Google CSE results from HTML"""
        results = []

        # Multiple patterns for CSE results
        patterns = [
            r'<a[^>]+href="([^"]*illawarramercury\.com\.au[^"]*)"[^>]*>([^<]+)</a>',
            r'href="(https://www\.illawarramercury\.com\.au/[^"]+)"[^>]*(?:title="([^"]*)")?',
            r'<h3[^>]*>.*?<a[^>]+href="([^"]*illawarramercury[^"]*)"[^>]*>([^<]+)</a>.*?</h3>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    url = match[0]
                    title = match[1] if len(
                        match) > 1 and match[1] else "Illawarra Mercury Article"
                else:
                    url = match
                    title = "Illawarra Mercury Article"

                # Clean and validate
                url = self._clean_url(url)
                title = self._clean_title(title)

                if url and self._is_valid_mercury_url(url):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=f"Found via {source} for query: {query}",
                        source=source,
                        confidence=0.9,
                        discovered_at=datetime.now().isoformat()
                    ))

        return results

    def _parse_google_results(self, html: str, query: str, source: str) -> List[SearchResult]:
        """Parse Google search results"""
        results = []

        # Google result patterns
        patterns = [
            r'<h3[^>]*><a[^>]+href="([^"]*illawarramercury\.com\.au[^"]*)"[^>]*>([^<]+)</a></h3>',
            r'<a[^>]+href="/url\?q=([^&]*illawarramercury\.com\.au[^&]*)[^"]*"[^>]*>.*?<h3[^>]*>([^<]+)</h3>',
            r'href="(https://www\.illawarramercury\.com\.au/[^"]*)"[^>]*><h3[^>]*>([^<]+)</h3>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for url, title in matches:
                url = self._clean_url(url)
                title = self._clean_title(title)

                if url and self._is_valid_mercury_url(url):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=f"Found via {source} for query: {query}",
                        source=source,
                        confidence=0.85,
                        discovered_at=datetime.now().isoformat()
                    ))

        return results

    def _parse_bing_results(self, html: str, query: str, source: str) -> List[SearchResult]:
        """Parse Bing search results"""
        results = []

        # Bing result patterns
        patterns = [
            r'<h2><a[^>]+href="([^"]*illawarramercury\.com\.au[^"]*)"[^>]*>([^<]+)</a></h2>',
            r'href="(https://www\.illawarramercury\.com\.au/[^"]*)"[^>]*>.*?<h2[^>]*>([^<]+)</h2>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for url, title in matches:
                url = self._clean_url(url)
                title = self._clean_title(title)

                if url and self._is_valid_mercury_url(url):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=f"Found via {source} for query: {query}",
                        source=source,
                        confidence=0.8,
                        discovered_at=datetime.now().isoformat()
                    ))

        return results

    def _parse_duckduckgo_results(self, html: str, query: str, source: str) -> List[SearchResult]:
        """Parse DuckDuckGo search results"""
        results = []

        # DuckDuckGo result patterns
        patterns = [
            r'<a[^>]+href="([^"]*illawarramercury\.com\.au[^"]*)"[^>]*class="result__a"[^>]*>([^<]+)</a>',
            r'href="(https://www\.illawarramercury\.com\.au/[^"]*)"[^>]*>.*?class="result__title"[^>]*>([^<]+)</[^>]*>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for url, title in matches:
                url = self._clean_url(url)
                title = self._clean_title(title)

                if url and self._is_valid_mercury_url(url):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=f"Found via {source} for query: {query}",
                        source=source,
                        confidence=0.75,
                        discovered_at=datetime.now().isoformat()
                    ))

        return results

    def _parse_website_search_results(self, html: str, query: str, source: str) -> List[SearchResult]:
        """Parse results from the website's own search functionality"""
        results = []

        # Look for article links in the HTML
        patterns = [
            r'<a[^>]+href="(/story/[^"]+)"[^>]*>([^<]+)</a>',
            r'href="(https://www\.illawarramercury\.com\.au/story/[^"]+)"[^>]*>([^<]+)',
            r'<h\d[^>]*><a[^>]+href="(/story/[^"]+)"[^>]*>([^<]+)</a></h\d>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for url, title in matches:
                if url.startswith('/'):
                    url = f"{self.base_url}{url}"

                url = self._clean_url(url)
                title = self._clean_title(title)

                if url and self._is_valid_mercury_url(url):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=f"Found via {source} for query: {query}",
                        source=source,
                        confidence=0.9,
                        discovered_at=datetime.now().isoformat()
                    ))

        return results

    def _parse_api_results(self, data: dict, query: str, source: str) -> List[SearchResult]:
        """Parse results from API JSON response"""
        results = []

        # Try different JSON structures
        items = data.get('items', data.get(
            'results', data.get('articles', [])))

        for item in items:
            title = item.get('title', item.get('headline', ''))
            url = item.get('url', item.get('link', item.get('permalink', '')))
            snippet = item.get('snippet', item.get(
                'summary', item.get('excerpt', '')))

            if title and url:
                if url.startswith('/'):
                    url = f"{self.base_url}{url}"

                url = self._clean_url(url)
                title = self._clean_title(title)

                if url and self._is_valid_mercury_url(url):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet or f"API result for query: {query}",
                        source=source,
                        confidence=0.95,
                        discovered_at=datetime.now().isoformat()
                    ))

        return results

    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ""

        # Remove Google redirect wrapper
        if '/url?q=' in url:
            match = re.search(r'/url\?q=([^&]+)', url)
            if match:
                url = match.group(1)

        # Decode URL
        try:
            from urllib.parse import unquote
            url = unquote(url)
        except:
            pass

        # Ensure proper protocol
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith('http'):
            if url.startswith('/'):
                url = self.base_url + url
            else:
                url = self.base_url + '/' + url

        return url.strip()

    def _clean_title(self, title: str) -> str:
        """Clean and normalize title"""
        if not title:
            return "Illawarra Mercury Article"

        # Remove HTML tags
        title = re.sub(r'<[^>]+>', '', title)

        # Decode HTML entities
        try:
            import html
            title = html.unescape(title)
        except:
            pass

        # Clean up whitespace
        title = re.sub(r'\s+', ' ', title).strip()

        return title

    def _is_valid_mercury_url(self, url: str) -> bool:
        """Check if URL is a valid Illawarra Mercury article URL"""
        return bool(url and 'illawarramercury.com.au' in url and '/story/' in url)

    def _extract_title_from_html(self, html: str) -> str:
        """Extract title from HTML content"""
        # Try multiple title patterns
        patterns = [
            r'<title>([^<]+)</title>',
            r'<h1[^>]*>([^<]+)</h1>',
            r'property="og:title"[^>]+content="([^"]+)"',
            r'name="title"[^>]+content="([^"]+)"'
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up common suffixes
                title = re.sub(r'\s*\|\s*.*$', '', title)
                title = re.sub(r'\s*-\s*Illawarra Mercury.*$', '', title)
                return title

        return "Illawarra Mercury Article"

    def _deduplicate_and_rank(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Remove duplicates and rank results by relevance and confidence"""
        seen_urls = set()
        unique_results = []

        # Sort by confidence first
        results.sort(key=lambda x: x.confidence, reverse=True)

        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)

                # Boost confidence if title contains query terms
                query_terms = query.lower().split()
                title_lower = result.title.lower()

                term_matches = sum(
                    1 for term in query_terms if term in title_lower)
                if term_matches > 0:
                    result.confidence += (term_matches /
                                          len(query_terms)) * 0.1

                unique_results.append(result)

        # Final sort by confidence
        unique_results.sort(key=lambda x: x.confidence, reverse=True)

        return unique_results

    def _cache_results(self, query: str, results: List[SearchResult]):
        """Cache search results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for result in results:
                cursor.execute('''
                    INSERT OR REPLACE INTO enhanced_search_results 
                    (query, title, url, snippet, source, confidence, discovered_at, last_verified, is_accessible)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    query, result.title, result.url, result.snippet,
                    result.source, result.confidence, result.discovered_at,
                    datetime.now().isoformat(), 1
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Cache error: {e}")


def main():
    """Test the enhanced intelligent finder"""
    finder = EnhancedIntelligentFinder()

    print("🚀 Enhanced Intelligent Article Finder")
    print("Using discovered Google CSE configuration")
    print(f"CSE ID: {finder.cse_id}")
    print("=" * 60)

    # Test queries
    test_queries = [
        "shellharbour council",
        "wollongong news today",
        "illawarra events",
        "local business news",
        "covid restrictions"
    ]

    for query in test_queries:
        print(f"\n🔍 Comprehensive search: '{query}'")
        print("=" * 50)

        results = finder.search_comprehensive(query, max_results=10)

        if results:
            print(f"\n✅ Found {len(results)} high-quality results:")
            print("-" * 40)

            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Source: {result.source}")
                print(f"   Confidence: {result.confidence:.2f}")
                print(f"   Snippet: {result.snippet[:100]}...")
                print()
        else:
            print("❌ No results found")

        print("\n" + "="*60)

        # Small delay between searches
        time.sleep(3)


if __name__ == "__main__":
    main()
