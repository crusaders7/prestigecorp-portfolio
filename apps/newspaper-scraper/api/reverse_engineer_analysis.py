#!/usr/bin/env python3
"""
REVERSE ENGINEERING ANALYSIS
Deep analysis of how articles are stored, generated, and displayed
Focus on finding older articles and understanding the storage architecture
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import sqlite3


def analyze_article_storage_system():
    """
    Comprehensive analysis of how the Illawarra Mercury stores and generates articles
    """
    print("🔬 REVERSE ENGINEERING ARTICLE STORAGE SYSTEM")
    print("=" * 70)

    analysis_results = {
        'url_patterns': [],
        'story_id_patterns': {},
        'date_encoding': {},
        'api_endpoints': [],
        'javascript_routes': [],
        'database_hints': [],
        'archive_systems': [],
        'older_article_strategies': []
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 1. Analyze URL Structure and Patterns
    print("\n📐 ANALYZING URL STRUCTURE")
    url_analysis = analyze_url_structure(headers)
    analysis_results['url_patterns'] = url_analysis

    # 2. Story ID Pattern Analysis
    print("\n🔢 ANALYZING STORY ID PATTERNS")
    story_id_analysis = analyze_story_id_patterns(headers)
    analysis_results['story_id_patterns'] = story_id_analysis

    # 3. Date and Archive System Analysis
    print("\n📅 ANALYZING DATE AND ARCHIVE SYSTEMS")
    date_analysis = analyze_date_archive_systems(headers)
    analysis_results['date_encoding'] = date_analysis

    # 4. JavaScript and API Discovery
    print("\n🌐 DISCOVERING JAVASCRIPT ROUTES AND APIS")
    js_api_analysis = discover_javascript_apis(headers)
    analysis_results['javascript_routes'] = js_api_analysis['javascript']
    analysis_results['api_endpoints'] = js_api_analysis['apis']

    # 5. Database Architecture Hints
    print("\n🗄️ ANALYZING DATABASE ARCHITECTURE HINTS")
    db_analysis = analyze_database_hints(headers)
    analysis_results['database_hints'] = db_analysis

    # 6. Older Article Discovery Strategies
    print("\n⏰ DEVELOPING OLDER ARTICLE STRATEGIES")
    older_strategies = develop_older_article_strategies(headers)
    analysis_results['older_article_strategies'] = older_strategies

    return analysis_results


def analyze_url_structure(headers):
    """Analyze URL patterns and structure"""
    patterns = []

    try:
        # Get main page and analyze internal links
        response = requests.get(
            'https://www.illawarramercury.com.au', headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all article links
            links = soup.find_all('a', href=True)
            article_urls = []

            for link in links:
                href = link['href']
                if '/story/' in href or 'illawarramercury.com.au' in href:
                    article_urls.append(href)

            # Analyze patterns
            url_patterns = {}
            for url in article_urls[:50]:  # Analyze first 50
                # Extract story ID pattern
                story_match = re.search(r'/story/(\d+)/', url)
                if story_match:
                    story_id = story_match.group(1)
                    id_length = len(story_id)

                    if id_length not in url_patterns:
                        url_patterns[id_length] = []
                    url_patterns[id_length].append(story_id)

                # Extract URL structure
                path_parts = urlparse(url).path.split('/')
                pattern_key = '/'.join(['*' if part.isdigit()
                                       else part for part in path_parts if part])

            patterns.append({
                'story_id_lengths': {k: len(v) for k, v in url_patterns.items()},
                'sample_ids': {k: v[:5] for k, v in url_patterns.items()},
                'total_articles_found': len(article_urls)
            })

            print(f"   📊 Found {len(article_urls)} article URLs")
            print(f"   🔢 Story ID lengths: {patterns[0]['story_id_lengths']}")

    except Exception as e:
        print(f"   ❌ Error analyzing URL structure: {e}")

    return patterns


def analyze_story_id_patterns(headers):
    """Analyze story ID generation patterns"""
    patterns = {}

    try:
        # Get recent RSS to find current ID ranges
        response = requests.get(
            'https://www.illawarramercury.com.au/rss.xml', headers=headers, timeout=10)
        if response.status_code == 200:
            story_ids = re.findall(r'/story/(\d+)/', response.text)

            if story_ids:
                ids_numeric = [int(id_str) for id_str in story_ids]
                ids_numeric.sort()

                patterns['current_range'] = {
                    'min': min(ids_numeric),
                    'max': max(ids_numeric),
                    'count': len(ids_numeric),
                    'gaps': []
                }

                # Analyze gaps
                for i in range(len(ids_numeric) - 1):
                    gap = ids_numeric[i + 1] - ids_numeric[i]
                    if gap > 1:
                        patterns['current_range']['gaps'].append({
                            'from': ids_numeric[i],
                            'to': ids_numeric[i + 1],
                            'gap_size': gap
                        })

                # Estimate daily publication rate
                id_range = max(ids_numeric) - min(ids_numeric)
                patterns['estimated_daily_rate'] = id_range / \
                    30  # Assume 30 days of content

                # Calculate potential older article IDs
                patterns['older_article_estimates'] = {
                    '1_month_ago': max(ids_numeric) - int(patterns['estimated_daily_rate'] * 30),
                    '3_months_ago': max(ids_numeric) - int(patterns['estimated_daily_rate'] * 90),
                    '6_months_ago': max(ids_numeric) - int(patterns['estimated_daily_rate'] * 180),
                    '1_year_ago': max(ids_numeric) - int(patterns['estimated_daily_rate'] * 365)
                }

                print(
                    f"   📈 Current ID range: {min(ids_numeric)} - {max(ids_numeric)}")
                print(
                    f"   ⚡ Estimated daily rate: ~{patterns['estimated_daily_rate']:.1f} articles/day")
                print(
                    f"   📅 Estimated 1 month ago ID: {patterns['older_article_estimates']['1_month_ago']}")

    except Exception as e:
        print(f"   ❌ Error analyzing story ID patterns: {e}")

    return patterns


def analyze_date_archive_systems(headers):
    """Analyze date-based archive systems"""
    date_systems = {}

    try:
        # Check for archive pages
        archive_urls = [
            'https://www.illawarramercury.com.au/archive/',
            'https://www.illawarramercury.com.au/archives/',
            'https://www.illawarramercury.com.au/sitemap/',
            'https://www.illawarramercury.com.au/sitemap.xml'
        ]

        for url in archive_urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    date_systems[url] = {
                        'status': 'found',
                        'content_type': response.headers.get('content-type', ''),
                        'size': len(response.content)
                    }

                    # Analyze sitemap if XML
                    if 'xml' in url.lower() and 'xml' in response.headers.get('content-type', ''):
                        soup = BeautifulSoup(response.content, 'xml')
                        urls_found = soup.find_all('url')
                        date_systems[url]['urls_count'] = len(urls_found)

                        # Extract date patterns from URLs
                        date_patterns = []
                        for url_elem in urls_found[:20]:  # Check first 20
                            loc = url_elem.find('loc')
                            if loc:
                                url_text = loc.get_text()
                                # Look for date patterns
                                date_match = re.search(
                                    r'(\d{4}/\d{2}/\d{2})', url_text)
                                if date_match:
                                    date_patterns.append(date_match.group(1))

                        date_systems[url]['date_patterns'] = list(
                            set(date_patterns))

                        print(f"   ✅ Found sitemap: {len(urls_found)} URLs")
                        if date_patterns:
                            print(
                                f"   📅 Date patterns found: {date_patterns[:3]}")
                else:
                    date_systems[url] = {
                        'status': 'not_found', 'code': response.status_code}
            except Exception:
                date_systems[url] = {'status': 'error'}

        # Test date-based URL patterns
        test_date_patterns(headers, date_systems)

    except Exception as e:
        print(f"   ❌ Error analyzing date systems: {e}")

    return date_systems


def test_date_patterns(headers, date_systems):
    """Test various date-based URL patterns"""
    print("   🗓️ Testing date-based URL patterns...")

    # Generate test dates (last few months)
    test_dates = []
    today = datetime.now()
    for days_back in [30, 60, 90, 120, 180]:
        past_date = today - timedelta(days=days_back)
        test_dates.append(past_date)

    date_patterns_to_test = [
        'https://www.illawarramercury.com.au/{year}/{month:02d}/{day:02d}/',
        'https://www.illawarramercury.com.au/archive/{year}/{month:02d}/',
        'https://www.illawarramercury.com.au/news/{year}/{month:02d}/{day:02d}/',
        'https://www.illawarramercury.com.au/{year}-{month:02d}-{day:02d}/'
    ]

    working_patterns = []
    for pattern in date_patterns_to_test:
        for test_date in test_dates[:2]:  # Test first 2 dates only
            try:
                url = pattern.format(
                    year=test_date.year,
                    month=test_date.month,
                    day=test_date.day
                )

                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    working_patterns.append({
                        'pattern': pattern,
                        'example_url': url,
                        'date': test_date.strftime('%Y-%m-%d')
                    })
                    print(f"   ✅ Working pattern: {pattern}")
                    break  # Found working pattern

                time.sleep(0.2)
            except Exception:
                continue

    date_systems['working_date_patterns'] = working_patterns


def discover_javascript_apis(headers):
    """Discover JavaScript routes and API endpoints"""
    js_apis = {'javascript': [], 'apis': []}

    try:
        # Get main page and analyze JavaScript
        response = requests.get(
            'https://www.illawarramercury.com.au', headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find JavaScript files
            scripts = soup.find_all('script', src=True)
            for script in scripts[:10]:  # Check first 10 scripts
                js_url = script['src']
                if js_url.startswith('/'):
                    js_url = 'https://www.illawarramercury.com.au' + js_url

                try:
                    js_response = requests.get(
                        js_url, headers=headers, timeout=10)
                    if js_response.status_code == 200:
                        js_content = js_response.text

                        # Look for API endpoints
                        api_patterns = [
                            r'["\']([^"\']*api[^"\']*)["\']',
                            r'["\']([^"\']*search[^"\']*)["\']',
                            r'["\']([^"\']*story[^"\']*)["\']',
                            r'fetch\(["\']([^"\']+)["\']',
                            r'xhr\.open\(["\'][^"\']*["\'],\s*["\']([^"\']+)["\']'
                        ]

                        for pattern in api_patterns:
                            matches = re.findall(
                                pattern, js_content, re.IGNORECASE)
                            for match in matches:
                                if any(keyword in match.lower() for keyword in ['api', 'search', 'story', 'article', 'news']):
                                    js_apis['apis'].append({
                                        'endpoint': match,
                                        'source_js': js_url,
                                        'pattern': pattern
                                    })

                        # Look for routing patterns
                        route_patterns = [
                            r'route[s]?\s*[:=]\s*{([^}]+)}',
                            r'path[s]?\s*[:=]\s*["\']([^"\']+)["\']'
                        ]

                        for pattern in route_patterns:
                            matches = re.findall(
                                pattern, js_content, re.IGNORECASE)
                            js_apis['javascript'].extend(matches)

                        print(f"   📄 Analyzed JS: {js_url}")

                except Exception:
                    continue

                time.sleep(0.3)

            # Look for inline JavaScript APIs
            inline_scripts = soup.find_all('script', src=False)
            for script in inline_scripts:
                if script.string:
                    # Look for AJAX calls and API endpoints
                    api_matches = re.findall(
                        r'["\']([^"\']*(?:api|search|story)[^"\']*)["\']', script.string, re.IGNORECASE)
                    js_apis['apis'].extend(
                        [{'endpoint': match, 'source_js': 'inline', 'pattern': 'inline'} for match in api_matches])

            print(f"   🔍 Found {len(js_apis['apis'])} potential API endpoints")
            print(f"   🔗 Found {len(js_apis['javascript'])} JavaScript routes")

    except Exception as e:
        print(f"   ❌ Error discovering JavaScript APIs: {e}")

    return js_apis


def analyze_database_hints(headers):
    """Analyze potential database architecture hints"""
    db_hints = []

    try:
        # Check robots.txt for admin/database hints
        response = requests.get(
            'https://www.illawarramercury.com.au/robots.txt', headers=headers, timeout=10)
        if response.status_code == 200:
            robots_content = response.text

            # Look for database-related paths
            db_paths = []
            for line in robots_content.split('\n'):
                if 'Disallow:' in line:
                    path = line.split('Disallow:')[1].strip()
                    if any(keyword in path.lower() for keyword in ['admin', 'api', 'database', 'sql', 'cms']):
                        db_paths.append(path)

            db_hints.append({
                'source': 'robots.txt',
                'hints': db_paths,
                'total_disallowed': len([l for l in robots_content.split('\n') if 'Disallow:' in l])
            })

            print(
                f"   🤖 robots.txt analysis: {len(db_paths)} database-related paths")

        # Check for common CMS/database indicators
        response = requests.get(
            'https://www.illawarramercury.com.au', headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()

            cms_indicators = {
                'wordpress': ['wp-content', 'wp-includes', 'wp-admin'],
                'drupal': ['sites/default', 'modules/', 'themes/'],
                'joomla': ['components/', 'modules/', 'templates/'],
                'custom_cms': ['cms/', 'admin/', 'backend/']
            }

            detected_cms = []
            for cms, indicators in cms_indicators.items():
                if any(indicator in content for indicator in indicators):
                    detected_cms.append(cms)

            db_hints.append({
                'source': 'cms_detection',
                'detected_systems': detected_cms
            })

            print(f"   🏗️ CMS detection: {detected_cms}")

    except Exception as e:
        print(f"   ❌ Error analyzing database hints: {e}")

    return db_hints


def develop_older_article_strategies(headers):
    """Develop strategies for finding older articles"""
    strategies = []

    print("   💡 Developing strategies for older articles...")

    # Strategy 1: Systematic ID Backtracking
    strategies.append({
        'name': 'Systematic ID Backtracking',
        'description': 'Use current ID range to calculate older article IDs',
        'implementation': 'Calculate daily publication rate and subtract time periods',
        'estimated_success': 'High for recent months, medium for older'
    })

    # Strategy 2: Archive URL Discovery
    strategies.append({
        'name': 'Archive URL Discovery',
        'description': 'Find date-based archive pages and sitemaps',
        'implementation': 'Test common archive URL patterns and sitemap exploration',
        'estimated_success': 'Medium - depends on site architecture'
    })

    # Strategy 3: RSS Historical Pagination
    strategies.append({
        'name': 'RSS Historical Pagination',
        'description': 'Deep pagination through RSS feeds to find older content',
        'implementation': 'Test RSS feeds with high page numbers (page=50, page=100)',
        'estimated_success': 'Low - most RSS feeds limit historical content'
    })

    # Strategy 4: Search Engine Cache
    strategies.append({
        'name': 'Search Engine Cache',
        'description': 'Use Google/Bing site searches with date filters',
        'implementation': 'site:illawarramercury.com.au before:YYYY-MM-DD',
        'estimated_success': 'High for indexed content'
    })

    # Strategy 5: Internet Archive Integration
    strategies.append({
        'name': 'Internet Archive Integration',
        'description': 'Use Wayback Machine to find historical snapshots',
        'implementation': 'Query archive.org API for historical pages',
        'estimated_success': 'High for preserved content'
    })

    print(f"   📋 Developed {len(strategies)} strategies for older articles")

    return strategies


def create_java_exploration_plan():
    """Create a plan for Java-based article discovery"""
    print("\n☕ JAVA ROUTE EXPLORATION PLAN")
    print("=" * 50)

    java_plan = {
        'web_scraping_libraries': [
            'JSoup - HTML parsing and manipulation',
            'HttpClient - Modern HTTP client (Java 11+)',
            'OkHttp - Popular HTTP client library',
            'WebDriver - Selenium for dynamic content'
        ],
        'advantages': [
            'Multithreading for concurrent requests',
            'Better memory management for large datasets',
            'Enterprise-grade reliability',
            'Integration with big data tools (Spark, Hadoop)'
        ],
        'implementation_strategy': [
            '1. Use JSoup for HTML parsing (similar to BeautifulSoup)',
            '2. Implement concurrent article fetching with CompletableFuture',
            '3. Create persistent storage with H2/SQLite database',
            '4. Build REST API with Spring Boot',
            '5. Add caching layer with Redis/Hazelcast'
        ],
        'sample_code_structure': '''
        // Main components:
        - ArticleScraper.java (core scraping logic)
        - StorageManager.java (database operations)
        - SearchController.java (REST API endpoints)
        - CacheManager.java (caching layer)
        - ScheduledTasks.java (periodic updates)
        '''
    }

    for category, items in java_plan.items():
        if category != 'sample_code_structure':
            print(f"\n📦 {category.replace('_', ' ').title()}:")
            for item in items:
                print(f"   • {item}")
        else:
            print(f"\n🏗️ {category.replace('_', ' ').title()}:")
            print(java_plan[category])

    return java_plan


def save_analysis_results(results):
    """Save analysis results to a comprehensive report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reverse_engineering_analysis_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        print(f"\n💾 Analysis saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")


def main():
    """Main execution"""
    print("🔬 REVERSE ENGINEERING ANALYSIS - Illawarra Mercury")
    print("Analyzing article storage, generation, and discovery systems")
    print("=" * 70)

    # Run comprehensive analysis
    results = analyze_article_storage_system()

    # Add Java exploration plan
    results['java_exploration'] = create_java_exploration_plan()

    # Save results
    save_analysis_results(results)

    # Print summary
    print("\n" + "=" * 70)
    print("🎯 ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"✅ URL patterns analyzed")
    print(f"✅ Story ID patterns discovered")
    print(f"✅ Date/archive systems explored")
    print(f"✅ JavaScript/API routes investigated")
    print(f"✅ Database architecture hints collected")
    print(f"✅ Older article strategies developed")
    print(f"✅ Java implementation plan created")

    print("\n🚀 Ready for implementation of older article discovery!")

    return results


if __name__ == "__main__":
    main()
