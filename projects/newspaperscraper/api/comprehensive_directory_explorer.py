#!/usr/bin/env python3
"""
Advanced Directory Structure Discovery for Illawarra Mercury
Find parent directories, category owners, and explore all accessible paths
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import re
import time
import json
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

class DirectoryExplorer:
    def __init__(self):
        self.base_url = "https://www.illawarramercury.com.au"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.discovered_paths = set()
        self.working_directories = {}
        self.category_hierarchy = defaultdict(list)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def explore_parent_directories(self, known_categories):
        """Explore parent directories of known working categories"""
        print("🔍 EXPLORING PARENT DIRECTORIES")
        print("=" * 60)
        
        parent_dirs = set()
        
        for category_url in known_categories:
            path = urlparse(category_url).path
            if path and path != '/':
                # Get all parent paths
                path_parts = [p for p in path.split('/') if p]
                
                # Build parent paths progressively
                for i in range(1, len(path_parts) + 1):
                    parent_path = '/' + '/'.join(path_parts[:i]) + '/'
                    parent_url = self.base_url + parent_path
                    parent_dirs.add(parent_url)
                    
                    # Also try without trailing slash
                    parent_path_no_slash = '/' + '/'.join(path_parts[:i])
                    parent_url_no_slash = self.base_url + parent_path_no_slash
                    parent_dirs.add(parent_url_no_slash)
        
        print(f"Found {len(parent_dirs)} potential parent directories")
        
        working_parents = []
        
        for parent_url in sorted(parent_dirs):
            try:
                response = self.session.get(parent_url, timeout=8)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Count content
                    story_links = soup.find_all('a', href=lambda x: x and '/story/' in x)
                    content_divs = soup.find_all(['div', 'article'], class_=re.compile(r'story|article|content', re.I))
                    
                    total_content = len(story_links) + len(content_divs)
                    
                    if total_content > 0:
                        working_parents.append({
                            'url': parent_url,
                            'path': urlparse(parent_url).path,
                            'stories': len(story_links),
                            'content_elements': len(content_divs),
                            'total_score': total_content
                        })
                        print(f"✅ {urlparse(parent_url).path:<30} - {len(story_links)} stories, {total_content} total content")
                        
                        # Look for category links within this parent
                        self.discover_subcategories_from_page(parent_url, soup)
                    else:
                        print(f"⚪ {urlparse(parent_url).path:<30} - No content")
                else:
                    print(f"❌ {urlparse(parent_url).path:<30} - Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {urlparse(parent_url).path:<30} - Error: {str(e)[:30]}...")
            
            time.sleep(0.1)
        
        return working_parents
    
    def discover_subcategories_from_page(self, parent_url, soup):
        """Discover subcategories from a parent page"""
        parent_path = urlparse(parent_url).path.rstrip('/')
        
        # Look for navigation elements and category links
        nav_selectors = [
            'nav a[href]',
            '.menu a[href]',
            '.category a[href]',
            '.section a[href]',
            '.nav a[href]',
            'ul.menu a[href]',
            '.sidebar a[href]'
        ]
        
        subcategories = []
        
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href.startswith('/') and parent_path in href and href != parent_path:
                    full_url = urljoin(self.base_url, href)
                    text = link.get_text().strip()
                    
                    if len(text) > 0 and full_url not in self.discovered_paths:
                        subcategories.append({
                            'parent': parent_url,
                            'url': full_url,
                            'path': href,
                            'text': text
                        })
                        self.discovered_paths.add(full_url)
        
        if subcategories:
            print(f"   📁 Found {len(subcategories)} subcategories in {parent_path}")
            for sub in subcategories[:5]:  # Show first 5
                print(f"      - {sub['text']}: {sub['path']}")
        
        return subcategories
    
    def explore_directory_permissions(self):
        """Test directory traversal and permissions"""
        print("\n🔐 EXPLORING DIRECTORY PERMISSIONS")
        print("=" * 60)
        
        # Test common directory patterns
        test_paths = [
            '/',
            '/news',
            '/sport', 
            '/entertainment',
            '/lifestyle',
            '/community',
            '/business',
            '/local',
            '/regional',
            '/archives',
            '/category',
            '/categories',
            '/section',
            '/sections',
            '/topics',
            '/tags',
            '/author',
            '/authors',
            '/feed',
            '/rss',
            '/api',
            '/content',
            '/admin',
            '/wp-content',
            '/wp-admin',
            '/assets',
            '/static',
            '/media',
            '/uploads',
            '/files'
        ]
        
        accessible_dirs = []
        
        for path in test_paths:
            test_url = self.base_url + path
            try:
                response = self.session.get(test_url, timeout=5)
                status = response.status_code
                
                if status == 200:
                    # Check if it's a directory listing or has content
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Look for directory listing indicators
                    is_directory = any([
                        'Index of' in response.text,
                        'Directory listing' in response.text,
                        len(soup.find_all('a', href=True)) > 10,  # Many links suggest directory
                        soup.find('title') and 'directory' in soup.find('title').get_text().lower()
                    ])
                    
                    # Count content
                    story_links = len(soup.find_all('a', href=lambda x: x and '/story/' in x))
                    content_score = story_links + len(soup.find_all(['article', 'div'], class_=re.compile(r'content|story', re.I)))
                    
                    accessible_dirs.append({
                        'path': path,
                        'url': test_url,
                        'status': status,
                        'is_directory': is_directory,
                        'content_score': content_score,
                        'story_count': story_links
                    })
                    
                    dir_type = "📁 Directory" if is_directory else "📄 Content"
                    print(f"✅ {path:<20} - {dir_type}, Score: {content_score}")
                    
                elif status == 403:
                    print(f"🔒 {path:<20} - Forbidden (directory exists)")
                    accessible_dirs.append({
                        'path': path,
                        'url': test_url,
                        'status': status,
                        'is_directory': True,
                        'access': 'forbidden'
                    })
                elif status == 301 or status == 302:
                    print(f"🔄 {path:<20} - Redirect (Status {status})")
                    # Follow redirect
                    try:
                        final_response = self.session.get(test_url, timeout=5, allow_redirects=True)
                        if final_response.status_code == 200:
                            print(f"   └─ Redirects to: {final_response.url}")
                    except:
                        pass
                else:
                    print(f"❌ {path:<20} - Status {status}")
                    
            except Exception as e:
                print(f"❌ {path:<20} - Error: {str(e)[:30]}...")
            
            time.sleep(0.1)
        
        return accessible_dirs
    
    def deep_crawl_categories(self, seed_urls, max_depth=3):
        """Perform deep crawling to find all category structures"""
        print(f"\n🕷️  DEEP CRAWLING CATEGORIES (Max depth: {max_depth})")
        print("=" * 60)
        
        visited = set()
        queue = deque([(url, 0) for url in seed_urls])
        found_categories = []
        
        while queue:
            current_url, depth = queue.popleft()
            
            if current_url in visited or depth > max_depth:
                continue
                
            visited.add(current_url)
            
            try:
                response = self.session.get(current_url, timeout=8)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Count content
                    story_links = soup.find_all('a', href=lambda x: x and '/story/' in x)
                    story_count = len(story_links)
                    
                    if story_count > 5:  # Only consider pages with substantial content
                        path = urlparse(current_url).path
                        found_categories.append({
                            'url': current_url,
                            'path': path,
                            'depth': depth,
                            'story_count': story_count,
                            'parent': None if depth == 0 else 'seed'
                        })
                        
                        print(f"{'  ' * depth}📂 {path} (depth {depth}) - {story_count} stories")
                        
                        # Find category/navigation links for next level
                        if depth < max_depth:
                            category_links = self.extract_category_links(soup, current_url)
                            for link in category_links:
                                if link not in visited:
                                    queue.append((link, depth + 1))
                
            except Exception as e:
                print(f"{'  ' * depth}❌ {current_url} - Error: {str(e)[:30]}...")
            
            time.sleep(0.2)
        
        return found_categories
    
    def extract_category_links(self, soup, base_url):
        """Extract potential category links from a page"""
        category_links = []
        base_path = urlparse(base_url).path.rstrip('/')
        
        # Look for navigation and category patterns
        selectors = [
            'nav a[href^="/"]',
            '.menu a[href^="/"]', 
            '.category a[href^="/"]',
            '.section a[href^="/"]',
            'ul.nav a[href^="/"]',
            '.sidebar a[href^="/"]',
            'a[href*="category"]',
            'a[href*="section"]',
            'a[href*="topic"]'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href.startswith('/'):
                    # Filter for likely category URLs
                    if any(pattern in href.lower() for pattern in [
                        '/news/', '/sport/', '/business/', '/lifestyle/', 
                        '/entertainment/', '/community/', '/local/', '/health/',
                        '/education/', '/environment/', '/politics/', '/crime/'
                    ]):
                        full_url = urljoin(self.base_url, href)
                        if full_url != base_url:  # Don't add self
                            category_links.append(full_url)
        
        return list(set(category_links))  # Remove duplicates
    
    def analyze_url_patterns(self):
        """Analyze URL patterns to predict more categories"""
        print("\n🔍 ANALYZING URL PATTERNS FOR PREDICTIONS")
        print("=" * 60)
        
        # Known working patterns
        working_patterns = [
            '/news/{topic}/',
            '/sport/{topic}/',
            '/entertainment/{topic}/',
            '/lifestyle/{topic}/',
            '/news/{location}/',
            '/sport/{sport}/',
            '/{topic}/'
        ]
        
        # Common news topics
        topics = [
            'breaking', 'local', 'national', 'international', 'world',
            'politics', 'government', 'election', 'council', 'court',
            'crime', 'police', 'business', 'economy', 'finance',
            'health', 'medical', 'hospital', 'education', 'school',
            'university', 'environment', 'climate', 'weather',
            'technology', 'digital', 'science', 'transport',
            'property', 'real-estate', 'development'
        ]
        
        # Sports
        sports = [
            'football', 'soccer', 'rugby', 'league', 'union', 'afl',
            'cricket', 'basketball', 'netball', 'tennis', 'golf',
            'swimming', 'athletics', 'cycling', 'motorsport', 'racing'
        ]
        
        # Local areas (Illawarra region)
        locations = [
            'wollongong', 'shellharbour', 'kiama', 'shoalhaven',
            'nowra', 'berry', 'gerringong', 'albion-park', 'dapto',
            'corrimal', 'fairy-meadow', 'thirroul', 'bulli',
            'helensburgh', 'sutherland-shire', 'southern-highlands'
        ]
        
        predicted_urls = []
        
        # Generate predictions
        for pattern in working_patterns:
            if '{topic}' in pattern:
                for topic in topics:
                    url = self.base_url + pattern.replace('{topic}', topic)
                    predicted_urls.append(url)
            
            if '{sport}' in pattern:
                for sport in sports:
                    url = self.base_url + pattern.replace('{sport}', sport)
                    predicted_urls.append(url)
                    
            if '{location}' in pattern:
                for location in locations:
                    url = self.base_url + pattern.replace('{location}', location)
                    predicted_urls.append(url)
        
        print(f"Generated {len(predicted_urls)} predicted URLs")
        
        # Test predictions
        working_predictions = []
        
        for i, url in enumerate(predicted_urls[:100]):  # Test first 100
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    story_count = len(soup.find_all('a', href=lambda x: x and '/story/' in x))
                    
                    if story_count > 3:
                        path = urlparse(url).path
                        working_predictions.append({
                            'url': url,
                            'path': path,
                            'story_count': story_count,
                            'prediction_type': 'pattern-based'
                        })
                        print(f"✅ {path:<40} - {story_count} stories")
                
            except Exception:
                pass
            
            if i % 20 == 0:
                print(f"   Tested {i + 1}/100 predictions...")
            time.sleep(0.1)
        
        return working_predictions
    
    def run_comprehensive_discovery(self):
        """Run all discovery methods"""
        print("🚀 COMPREHENSIVE DIRECTORY STRUCTURE DISCOVERY")
        print("=" * 70)
        
        all_discoveries = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'discoveries': {}
        }
        
        # Start with known working categories
        known_categories = [
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/entertainment/",
            "https://www.illawarramercury.com.au/lifestyle/",
            "https://www.illawarramercury.com.au/community/",
            "https://www.illawarramercury.com.au/news/local-news/",
            "https://www.illawarramercury.com.au/news/business/",
            "https://www.illawarramercury.com.au/news/politics/"
        ]
        
        # 1. Explore parent directories
        print("\n" + "=" * 70)
        parent_dirs = self.explore_parent_directories(known_categories)
        all_discoveries['discoveries']['parent_directories'] = parent_dirs
        
        # 2. Check directory permissions
        print("\n" + "=" * 70)
        accessible_dirs = self.explore_directory_permissions()
        all_discoveries['discoveries']['accessible_directories'] = accessible_dirs
        
        # 3. Deep crawl for categories
        print("\n" + "=" * 70)
        deep_categories = self.deep_crawl_categories(known_categories[:4], max_depth=2)  # Limit for speed
        all_discoveries['discoveries']['deep_crawl_categories'] = deep_categories
        
        # 4. Pattern-based predictions
        print("\n" + "=" * 70)
        predicted_categories = self.analyze_url_patterns()
        all_discoveries['discoveries']['predicted_categories'] = predicted_categories
        
        # Compile comprehensive results
        print(f"\n🎯 COMPREHENSIVE DISCOVERY RESULTS")
        print("=" * 70)
        
        all_working_categories = []
        
        # Collect all working categories
        for parent in parent_dirs:
            if parent['total_score'] > 5:
                all_working_categories.append(parent['url'])
        
        for directory in accessible_dirs:
            if directory.get('content_score', 0) > 5:
                all_working_categories.append(directory['url'])
        
        for category in deep_categories:
            all_working_categories.append(category['url'])
            
        for prediction in predicted_categories:
            all_working_categories.append(prediction['url'])
        
        # Remove duplicates and sort
        unique_categories = sorted(list(set(all_working_categories)))
        
        print(f"📊 FINAL STATISTICS:")
        print(f"   🔍 Parent directories found: {len([p for p in parent_dirs if p['total_score'] > 5])}")
        print(f"   🔐 Accessible directories: {len([d for d in accessible_dirs if d.get('content_score', 0) > 5])}")
        print(f"   🕷️  Deep crawl categories: {len(deep_categories)}")
        print(f"   🎯 Pattern predictions: {len(predicted_categories)}")
        print(f"   ✅ Total unique categories: {len(unique_categories)}")
        
        # Generate enhanced category list
        print(f"\n🚀 ENHANCED CATEGORY LIST:")
        print("=" * 70)
        print("# COMPREHENSIVE CATEGORY DISCOVERY - ALL WORKING DIRECTORIES")
        print("category_urls = [")
        
        for url in unique_categories:
            comment = self.get_category_description(url, all_discoveries)
            print(f'    "{url}",  {comment}')
        
        print("]")
        
        # Save comprehensive results
        all_discoveries['final_categories'] = unique_categories
        all_discoveries['total_count'] = len(unique_categories)
        
        with open('comprehensive_category_discovery.json', 'w') as f:
            json.dump(all_discoveries, f, indent=2)
        
        print(f"\n💾 Comprehensive results saved to comprehensive_category_discovery.json")
        print(f"🎉 Discovery complete! Found {len(unique_categories)} total working categories")
        
        return unique_categories
    
    def get_category_description(self, url, discoveries):
        """Get description for a category based on discovery method"""
        path = urlparse(url).path
        
        # Check which discovery method found this
        for parent in discoveries['discoveries'].get('parent_directories', []):
            if parent['url'] == url:
                return f"# Parent dir - {parent['stories']} stories"
        
        for directory in discoveries['discoveries'].get('accessible_directories', []):
            if directory['url'] == url:
                return f"# Accessible - {directory.get('story_count', 0)} stories"
        
        for category in discoveries['discoveries'].get('deep_crawl_categories', []):
            if category['url'] == url:
                return f"# Deep crawl - {category['story_count']} stories"
        
        for prediction in discoveries['discoveries'].get('predicted_categories', []):
            if prediction['url'] == url:
                return f"# Predicted - {prediction['story_count']} stories"
        
        return f"# Category - {path}"

if __name__ == "__main__":
    explorer = DirectoryExplorer()
    explorer.run_comprehensive_discovery()
