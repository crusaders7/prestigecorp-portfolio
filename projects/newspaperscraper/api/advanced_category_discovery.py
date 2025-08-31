#!/usr/bin/env python3
"""
Advanced Category Discovery for Illawarra Mercury
Find all possible categories and subcategories on the website
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
import json
from collections import defaultdict

def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'

class CategoryDiscovery:
    def __init__(self):
        self.base_url = "https://www.illawarramercury.com.au"
        self.headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.discovered_categories = {}
        self.tested_urls = set()
        
    def discover_from_navigation(self):
        """Extract categories from website navigation"""
        print("🧭 Discovering categories from navigation...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            categories = set()
            
            # Look for navigation elements
            nav_selectors = [
                'nav',
                '[class*="nav"]',
                '[class*="menu"]',
                '[class*="header"]',
                '[id*="nav"]',
                '[id*="menu"]'
            ]
            
            for selector in nav_selectors:
                nav_elements = soup.select(selector)
                for nav in nav_elements:
                    # Extract all links from navigation
                    for link in nav.find_all('a', href=True):
                        href = link['href']
                        text = link.get_text().strip()
                        
                        if href.startswith('/') and len(text) > 0 and len(href) > 1:
                            full_url = urljoin(self.base_url, href)
                            categories.add((text, full_url, href))
            
            print(f"   Found {len(categories)} navigation links")
            return categories
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return set()
    
    def discover_from_sitemap(self):
        """Try to find categories from sitemap"""
        print("🗺️  Checking for sitemap...")
        
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/robots.txt"
        ]
        
        categories = set()
        
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Found: {sitemap_url}")
                    
                    if 'robots.txt' in sitemap_url:
                        # Extract sitemap URLs from robots.txt
                        for line in response.text.split('\n'):
                            if 'sitemap' in line.lower():
                                print(f"   📋 Robots.txt entry: {line}")
                    else:
                        # Parse XML sitemap
                        soup = BeautifulSoup(response.content, 'xml')
                        urls = soup.find_all('loc')
                        for url_elem in urls:
                            url = url_elem.get_text()
                            if self.base_url in url:
                                path = urlparse(url).path
                                if len(path) > 1 and path != '/':
                                    categories.add(('Sitemap', url, path))
                        
                        print(f"   Found {len(urls)} URLs in sitemap")
                        
            except Exception as e:
                print(f"   ❌ {sitemap_url}: {e}")
        
        return categories
    
    def discover_pattern_based(self):
        """Test common category patterns"""
        print("🎯 Testing pattern-based categories...")
        
        # Comprehensive category patterns
        category_patterns = {
            # Main sections
            'news': ['/news/', '/news/local/', '/news/national/', '/news/international/', '/news/breaking/'],
            'sport': ['/sport/', '/sports/', '/sport/local/', '/sport/nrl/', '/sport/afl/', '/sport/rugby/', '/sport/football/', '/sport/soccer/', '/sport/cricket/', '/sport/basketball/', '/sport/netball/', '/sport/tennis/', '/sport/golf/', '/sport/racing/', '/sport/other/'],
            'business': ['/business/', '/economy/', '/finance/', '/money/', '/property/', '/real-estate/', '/jobs/', '/careers/'],
            'lifestyle': ['/lifestyle/', '/health/', '/fitness/', '/food/', '/recipes/', '/travel/', '/fashion/', '/beauty/', '/relationships/', '/parenting/', '/home/', '/garden/'],
            'entertainment': ['/entertainment/', '/movies/', '/tv/', '/music/', '/books/', '/arts/', '/culture/', '/celebrities/', '/events/'],
            'opinion': ['/opinion/', '/editorial/', '/letters/', '/blogs/', '/columnists/', '/commentary/'],
            'community': ['/community/', '/local/', '/events/', '/notices/', '/obituaries/', '/births/', '/deaths/', '/marriages/'],
            'education': ['/education/', '/schools/', '/university/', '/tafe/', '/training/'],
            'health': ['/health/', '/medical/', '/hospital/', '/wellness/', '/mental-health/'],
            'environment': ['/environment/', '/sustainability/', '/climate/', '/nature/', '/conservation/'],
            'technology': ['/technology/', '/tech/', '/digital/', '/internet/', '/gadgets/', '/innovation/'],
            'politics': ['/politics/', '/government/', '/council/', '/election/', '/voting/', '/policy/'],
            'crime': ['/crime/', '/police/', '/court/', '/legal/', '/justice/'],
            'weather': ['/weather/', '/forecast/', '/climate/', '/conditions/'],
            
            # Regional categories
            'regional': ['/illawarra/', '/wollongong/', '/shellharbour/', '/shoalhaven/', '/kiama/', '/nowra/', '/albion-park/', '/dapto/', '/corrimal/', '/fairy-meadow/', '/thirroul/', '/bulli/', '/helensburgh/', '/southern-highlands/', '/moss-vale/', '/bowral/'],
            
            # Special sections
            'special': ['/photos/', '/videos/', '/galleries/', '/multimedia/', '/podcasts/', '/newsletters/', '/competitions/', '/classifieds/', '/death-notices/', '/funeral-notices/']
        }
        
        working_categories = []
        
        for category_type, patterns in category_patterns.items():
            print(f"   🔍 Testing {category_type} patterns...")
            
            for pattern in patterns:
                if pattern in self.tested_urls:
                    continue
                    
                test_url = self.base_url + pattern
                self.tested_urls.add(pattern)
                
                try:
                    response = requests.get(test_url, headers=self.headers, timeout=8)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'lxml')
                        
                        # Count story links
                        story_links = soup.find_all('a', href=lambda x: x and '/story/' in x)
                        article_count = len(story_links)
                        
                        # Also check for other content indicators
                        content_indicators = len(soup.find_all(['article', 'div'], class_=re.compile(r'story|article|post', re.I)))
                        
                        total_content = article_count + content_indicators
                        
                        if total_content > 0:
                            working_categories.append({
                                'category_type': category_type,
                                'path': pattern,
                                'url': test_url,
                                'article_count': article_count,
                                'content_score': total_content
                            })
                            print(f"      ✅ {pattern:<25} - {article_count} articles, {total_content} total content")
                        else:
                            print(f"      ⚪ {pattern:<25} - No content")
                    else:
                        print(f"      ❌ {pattern:<25} - Status {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ {pattern:<25} - Error: {str(e)[:30]}...")
                
                time.sleep(0.2)  # Be respectful
        
        return working_categories
    
    def discover_from_existing_pages(self):
        """Crawl existing category pages to find more subcategories"""
        print("🕸️  Discovering subcategories from existing pages...")
        
        # Start with known working categories
        seed_categories = [
            "https://www.illawarramercury.com.au/news/",
            "https://www.illawarramercury.com.au/sport/",
            "https://www.illawarramercury.com.au/entertainment/",
            "https://www.illawarramercury.com.au/lifestyle/"
        ]
        
        discovered_subcategories = []
        
        for category_url in seed_categories:
            try:
                response = requests.get(category_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Look for subcategory links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        text = link.get_text().strip()
                        
                        if href.startswith('/') and category_url.split('/')[-2] in href:
                            # This looks like a subcategory
                            full_url = urljoin(self.base_url, href)
                            if full_url != category_url and full_url not in [cat['url'] for cat in discovered_subcategories]:
                                
                                # Quick test if it has content
                                try:
                                    test_response = requests.get(full_url, headers=self.headers, timeout=5)
                                    if test_response.status_code == 200:
                                        test_soup = BeautifulSoup(test_response.content, 'lxml')
                                        story_count = len(test_soup.find_all('a', href=lambda x: x and '/story/' in x))
                                        
                                        if story_count > 5:
                                            discovered_subcategories.append({
                                                'parent_category': category_url,
                                                'path': href,
                                                'url': full_url,
                                                'text': text,
                                                'article_count': story_count
                                            })
                                            print(f"   ✅ Found subcategory: {href} ({story_count} articles)")
                                
                                except Exception:
                                    pass
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error crawling {category_url}: {e}")
        
        return discovered_subcategories
    
    def test_category_depth(self, base_categories):
        """Test how deep category structures go"""
        print("🏗️  Testing category depth...")
        
        deep_categories = []
        
        for category in base_categories[:5]:  # Test first 5 to save time
            base_path = category['path'].rstrip('/')
            
            # Try adding common suffixes
            depth_patterns = [
                '/latest/',
                '/archive/',
                '/local/',
                '/regional/',
                '/breaking/',
                '/featured/',
                '/popular/',
                '/photos/',
                '/videos/'
            ]
            
            for suffix in depth_patterns:
                test_path = base_path + suffix
                test_url = self.base_url + test_path
                
                try:
                    response = requests.get(test_url, headers=self.headers, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'lxml')
                        story_count = len(soup.find_all('a', href=lambda x: x and '/story/' in x))
                        
                        if story_count > 3:
                            deep_categories.append({
                                'parent_path': base_path,
                                'path': test_path,
                                'url': test_url,
                                'article_count': story_count,
                                'depth': 2
                            })
                            print(f"   ✅ Deep category: {test_path} ({story_count} articles)")
                
                except Exception:
                    pass
                
                time.sleep(0.1)
        
        return deep_categories
    
    def run_full_discovery(self):
        """Run complete category discovery"""
        print("🚀 STARTING COMPREHENSIVE CATEGORY DISCOVERY")
        print("=" * 60)
        
        all_categories = []
        
        # Method 1: Navigation discovery
        nav_categories = self.discover_from_navigation()
        print(f"📊 Navigation discovery: {len(nav_categories)} found\n")
        
        # Method 2: Sitemap discovery
        sitemap_categories = self.discover_from_sitemap()
        print(f"📊 Sitemap discovery: {len(sitemap_categories)} found\n")
        
        # Method 3: Pattern-based discovery
        pattern_categories = self.discover_pattern_based()
        print(f"📊 Pattern discovery: {len(pattern_categories)} found\n")
        
        # Method 4: Subcategory discovery
        subcategories = self.discover_from_existing_pages()
        print(f"📊 Subcategory discovery: {len(subcategories)} found\n")
        
        # Method 5: Deep category testing
        deep_categories = self.test_category_depth(pattern_categories)
        print(f"📊 Deep category discovery: {len(deep_categories)} found\n")
        
        # Combine and analyze results
        print("📋 COMPREHENSIVE RESULTS")
        print("=" * 60)
        
        # Sort pattern categories by content score
        pattern_categories.sort(key=lambda x: x['content_score'], reverse=True)
        
        print("🏆 TOP WORKING CATEGORIES (by content):")
        print("-" * 60)
        
        category_list = []
        total_articles = 0
        
        for i, cat in enumerate(pattern_categories[:20], 1):  # Top 20
            total_articles += cat['article_count']
            category_list.append(cat['url'])
            print(f"{i:2d}. {cat['path']:<30} {cat['article_count']:>3} articles - {cat['category_type']}")
        
        # Add successful subcategories
        print(f"\n🌿 SUBCATEGORIES:")
        print("-" * 60)
        for sub in subcategories:
            if sub['article_count'] > 10:  # Only significant subcategories
                total_articles += sub['article_count']
                category_list.append(sub['url'])
                print(f"   {sub['path']:<30} {sub['article_count']:>3} articles")
        
        # Add deep categories
        print(f"\n🏗️  DEEP CATEGORIES:")
        print("-" * 60)
        for deep in deep_categories:
            if deep['article_count'] > 5:
                total_articles += deep['article_count']
                category_list.append(deep['url'])
                print(f"   {deep['path']:<30} {deep['article_count']:>3} articles")
        
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   ✅ Total working categories: {len(category_list)}")
        print(f"   📰 Total articles available: {total_articles}")
        print(f"   📈 Average per category: {total_articles/len(category_list):.1f}")
        
        # Generate the updated category list
        print(f"\n🚀 UPDATED CATEGORY LIST FOR search.py:")
        print("=" * 60)
        print("category_urls = [")
        
        # Deduplicate and sort by likely importance
        unique_categories = list(dict.fromkeys(category_list))  # Preserve order, remove duplicates
        
        for url in unique_categories:
            # Add comments for category type
            path = urlparse(url).path
            comment = ""
            for cat in pattern_categories:
                if cat['url'] == url:
                    comment = f"  # {cat['category_type']} - {cat['article_count']} articles"
                    break
            
            print(f'    "{url}",{comment}')
        
        print("]")
        
        # Save results to JSON for future reference
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_categories': len(unique_categories),
            'total_articles': total_articles,
            'categories': [
                {
                    'url': cat['url'],
                    'path': cat['path'],
                    'type': cat['category_type'],
                    'articles': cat['article_count'],
                    'content_score': cat['content_score']
                }
                for cat in pattern_categories
            ],
            'subcategories': subcategories,
            'deep_categories': deep_categories,
            'category_urls': unique_categories
        }
        
        with open('category_discovery_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to category_discovery_results.json")
        print(f"✅ Discovery complete! Found {len(unique_categories)} working categories")
        
        return unique_categories

if __name__ == "__main__":
    discovery = CategoryDiscovery()
    discovery.run_full_discovery()
