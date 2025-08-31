#!/usr/bin/env python3
"""
Deep Pagination Scanner for Missing Articles
Scans deeper into pagination of working categories to find missing articles
"""

import requests
from bs4 import BeautifulSoup
import re
import time

def scan_deep_pagination():
    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Working categories from our comprehensive discovery
    working_categories = [
        'https://www.illawarramercury.com.au/',  # Homepage - most promising
        'https://www.illawarramercury.com.au/sport/',
        'https://www.illawarramercury.com.au/news/',
        'https://www.illawarramercury.com.au/politics/',
        'https://www.illawarramercury.com.au/local-news/',
        'https://www.illawarramercury.com.au/local-sport/',
        'https://www.illawarramercury.com.au/community/',
    ]
    
    print('🔍 DEEP PAGINATION SCAN FOR MISSING ARTICLES')
    print('=' * 60)
    
    all_found = []
    
    for category in working_categories:
        print(f'\n📂 Scanning: {category}')
        
        for page in range(1, 11):  # Scan up to 10 pages deep
            page_url = f"{category}?page={page}" if page > 1 else category
            
            try:
                response = requests.get(page_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    if page == 1:
                        print(f'   ❌ Category not accessible: {response.status_code}')
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links
                article_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/story/' in href and 'illawarramercury.com.au' in href:
                        article_links.append(href)
                
                if not article_links:
                    if page == 1:
                        print(f'   ⚠️ No articles found on page {page}')
                    else:
                        print(f'   📄 Page {page}: End of pagination')
                    break
                
                # Check for target articles
                page_found = []
                for link in article_links:
                    for target_id in target_ids:
                        if target_id in link:
                            page_found.append((target_id, link))
                            all_found.append((target_id, link, category, page))
                
                if page_found:
                    print(f'   📄 Page {page}: {len(article_links)} articles - 🎯 FOUND {len(page_found)} TARGETS!')
                    for target_id, link in page_found:
                        print(f'      • {target_id}: {link}')
                else:
                    # Show sample IDs for context
                    story_ids = []
                    for link in article_links[:5]:
                        match = re.search(r'/story/(\d+)/', link)
                        if match:
                            story_ids.append(int(match.group(1)))
                    
                    if story_ids:
                        print(f'   📄 Page {page}: {len(article_links)} articles (IDs: {min(story_ids)}-{max(story_ids)})')
                    else:
                        print(f'   📄 Page {page}: {len(article_links)} articles')
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f'   ❌ Error on page {page}: {str(e)}')
                break
    
    print('\n' + '=' * 60)
    print('📊 DEEP SCAN RESULTS')
    print('=' * 60)
    
    if all_found:
        print(f'🎯 Found {len(all_found)} target articles:')
        for target_id, link, category, page in all_found:
            category_name = category.split('/')[-2] if category.endswith('/') else category.split('/')[-1]
            print(f'   • {target_id}: Page {page} of {category_name}')
            print(f'     URL: {link}')
    else:
        print('❌ No target articles found in deep pagination scan')
        print('💡 Articles might be in:')
        print('   • Search results pages')
        print('   • RSS feeds')
        print('   • Dynamic content (JavaScript-loaded)')
        print('   • Archive sections not in main navigation')
    
    return all_found

if __name__ == "__main__":
    found_articles = scan_deep_pagination()
