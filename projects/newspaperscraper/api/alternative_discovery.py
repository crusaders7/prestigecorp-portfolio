#!/usr/bin/env python3
"""
Alternative Discovery Methods for Missing Articles
Tests RSS feeds, search endpoints, and sitemap for missing articles
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time


def test_rss_feeds():
    """Test RSS feeds for articles"""
    print('\n🔗 TESTING RSS FEEDS')
    print('=' * 40)

    rss_urls = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/politics/rss.xml',
        'https://www.illawarramercury.com.au/feed/',
        'https://www.illawarramercury.com.au/rss/',
        'https://www.illawarramercury.com.au/feeds/news.xml',
    ]

    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found_articles = []

    for rss_url in rss_urls:
        print(f'\n📡 Testing: {rss_url}')
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f'   ✅ Accessible ({len(response.content)} bytes)')

                # Look for story URLs in RSS content
                content = response.text
                story_urls = re.findall(
                    r'https://www\.illawarramercury\.com\.au/story/\d+/[^<\s"]+', content)

                if story_urls:
                    print(f'   📰 Found {len(story_urls)} story URLs')

                    # Check for target articles
                    for url in story_urls:
                        for target_id in target_ids:
                            if target_id in url:
                                print(
                                    f'   🎯 FOUND TARGET: {target_id} in {url}')
                                found_articles.append((target_id, url))
                else:
                    print('   ⚠️ No story URLs found')
            else:
                print(f'   ❌ Status: {response.status_code}')
        except Exception as e:
            print(f'   ❌ Error: {str(e)}')

        time.sleep(0.5)

    return found_articles


def test_search_endpoints():
    """Test search endpoints"""
    print('\n🔍 TESTING SEARCH ENDPOINTS')
    print('=' * 40)

    search_terms = [
        'shellharbour council',
        'chris homer mayor',
        'tim banfield',
        'jock brown oval',
        'ceo sacking'
    ]

    search_endpoints = [
        'https://www.illawarramercury.com.au/search/',
        'https://www.illawarramercury.com.au/api/search',
        'https://www.illawarramercury.com.au/search.php',
        'https://search.illawarramercury.com.au/',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    found_articles = []

    for endpoint in search_endpoints:
        print(f'\n🔎 Testing endpoint: {endpoint}')
        for term in search_terms:
            try:
                # Try different search parameter formats
                search_params = [
                    {'q': term},
                    {'search': term},
                    {'query': term},
                    {'s': term}
                ]

                for params in search_params:
                    try:
                        response = requests.get(
                            endpoint, params=params, headers=headers, timeout=10)
                        if response.status_code == 200:
                            soup = BeautifulSoup(
                                response.content, 'html.parser')

                            # Look for story links
                            story_links = []
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                if '/story/' in href and 'illawarramercury.com.au' in href:
                                    story_links.append(href)

                            if story_links:
                                print(
                                    f'   📊 Found {len(story_links)} results for "{term}"')

                                # Check for targets
                                for link in story_links:
                                    for target_id in target_ids:
                                        if target_id in link:
                                            print(
                                                f'   🎯 FOUND TARGET: {target_id} in {link}')
                                            found_articles.append(
                                                (target_id, link))
                                break  # Found working parameter format

                    except Exception as e:
                        continue

            except Exception as e:
                continue

        time.sleep(1)

    return found_articles


def test_sitemap():
    """Test sitemap for articles"""
    print('\n🗺️ TESTING SITEMAP')
    print('=' * 40)

    sitemap_urls = [
        'https://www.illawarramercury.com.au/sitemap.xml',
        'https://www.illawarramercury.com.au/sitemap_index.xml',
        'https://www.illawarramercury.com.au/robots.txt',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    target_ids = ['9050660', '9046630', '9045329', '636609', '9044604']
    found_articles = []

    for sitemap_url in sitemap_urls:
        print(f'\n📋 Testing: {sitemap_url}')
        try:
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                print(f'   ✅ Accessible ({len(content)} chars)')

                # Look for story URLs
                story_urls = re.findall(
                    r'https://www\.illawarramercury\.com\.au/story/\d+/[^<\s"]+', content)

                if story_urls:
                    print(f'   📰 Found {len(story_urls)} story URLs')

                    # Check for targets
                    for url in story_urls:
                        for target_id in target_ids:
                            if target_id in url:
                                print(
                                    f'   🎯 FOUND TARGET: {target_id} in {url}')
                                found_articles.append((target_id, url))

                # Look for additional sitemaps
                additional_sitemaps = re.findall(
                    r'https://[^<\s"]+sitemap[^<\s"]*\.xml', content)
                if additional_sitemaps:
                    print(
                        f'   📂 Found {len(additional_sitemaps)} additional sitemaps')
                    for add_sitemap in additional_sitemaps[:5]:  # Test first 5
                        print(f'   📋 Testing additional: {add_sitemap}')
                        try:
                            add_response = requests.get(
                                add_sitemap, headers=headers, timeout=10)
                            if add_response.status_code == 200:
                                add_content = add_response.text
                                add_story_urls = re.findall(
                                    r'https://www\.illawarramercury\.com\.au/story/\d+/[^<\s"]+', add_content)
                                if add_story_urls:
                                    print(
                                        f'      📰 Found {len(add_story_urls)} additional stories')
                                    for url in add_story_urls:
                                        for target_id in target_ids:
                                            if target_id in url:
                                                print(
                                                    f'      🎯 FOUND TARGET: {target_id} in {url}')
                                                found_articles.append(
                                                    (target_id, url))
                        except:
                            continue
                        time.sleep(0.5)
            else:
                print(f'   ❌ Status: {response.status_code}')
        except Exception as e:
            print(f'   ❌ Error: {str(e)}')

        time.sleep(0.5)

    return found_articles


def main():
    print('🔍 ALTERNATIVE DISCOVERY METHODS')
    print('=' * 60)

    all_found = []

    # Test RSS feeds
    rss_found = test_rss_feeds()
    all_found.extend(rss_found)

    # Test search endpoints
    search_found = test_search_endpoints()
    all_found.extend(search_found)

    # Test sitemap
    sitemap_found = test_sitemap()
    all_found.extend(sitemap_found)

    print('\n' + '=' * 60)
    print('📊 ALTERNATIVE DISCOVERY RESULTS')
    print('=' * 60)

    if all_found:
        unique_found = list(set(all_found))  # Remove duplicates
        print(f'🎯 Found {len(unique_found)} unique target articles:')
        for target_id, url in unique_found:
            print(f'   • {target_id}: {url}')
    else:
        print('❌ No target articles found through alternative methods')
        print('\n💡 Next steps:')
        print('   • Check if articles are behind authentication')
        print('   • Test with browser automation (Selenium)')
        print('   • Check for JavaScript-rendered content')
        print('   • Verify articles still exist on the site')


if __name__ == "__main__":
    main()
