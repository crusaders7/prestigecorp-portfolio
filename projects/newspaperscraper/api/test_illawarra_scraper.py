#!/usr/bin/env python3
"""
Test script for Illawarra Mercury scraping strategies
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, quote_plus

def test_search_strategies(query="shellharbour council"):
    """Test multiple search strategies"""
    print(f"=== Testing Search Strategies for '{query}' ===\n")
    
    strategies = [
        test_direct_search,
        test_google_search,
        test_bing_search,
        test_homepage_scraping
    ]
    
    all_results = []
    
    for strategy in strategies:
        try:
            results = strategy(query)
            all_results.extend(results)
            time.sleep(2)  # Be respectful
        except Exception as e:
            print(f"Strategy {strategy.__name__} failed: {e}\n")
    
    # Remove duplicates
    unique_results = list(dict.fromkeys(all_results))
    
    print(f"=== TOTAL UNIQUE RESULTS: {len(unique_results)} ===")
    for i, url in enumerate(unique_results[:10], 1):
        print(f"{i}. {url}")
    
    return unique_results

def test_direct_search(query):
    """Test direct search on Illawarra Mercury"""
    print("1. Testing Direct Search...")
    
    search_url = f"https://www.illawarramercury.com.au/search/?q={quote_plus(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Multiple selectors to try
        selectors = [
            'a[href*="/story/"]',
            '.story-block a',
            '.search-result a',
            'article a',
            '.article-link'
        ]
        
        urls = []
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/story/' in href:
                    full_url = urljoin("https://www.illawarramercury.com.au", href)
                    if full_url not in urls:
                        urls.append(full_url)
        
        print(f"   Found {len(urls)} articles via direct search")
        return urls[:10]
        
    except Exception as e:
        print(f"   Direct search failed: {e}")
        return []

def test_google_search(query):
    """Test Google search for Illawarra Mercury articles"""
    print("2. Testing Google Search...")
    
    search_query = f"site:illawarramercury.com.au {query}"
    google_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(google_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        urls = []
        # Look for Google result links
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/url?q=' in href:
                # Extract actual URL from Google redirect
                match = re.search(r'/url\?q=([^&]+)', href)
                if match:
                    actual_url = match.group(1)
                    if 'illawarramercury.com.au/story/' in actual_url:
                        urls.append(actual_url)
        
        print(f"   Found {len(urls)} articles via Google search")
        return urls[:10]
        
    except Exception as e:
        print(f"   Google search failed: {e}")
        return []

def test_bing_search(query):
    """Test Bing search for Illawarra Mercury articles"""
    print("3. Testing Bing Search...")
    
    search_query = f"site:illawarramercury.com.au {query}"
    bing_url = f"https://www.bing.com/search?q={quote_plus(search_query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(bing_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        urls = []
        # Look for Bing result links
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'illawarramercury.com.au/story/' in href:
                urls.append(href)
        
        print(f"   Found {len(urls)} articles via Bing search")
        return urls[:10]
        
    except Exception as e:
        print(f"   Bing search failed: {e}")
        return []

def test_homepage_scraping(query):
    """Test scraping from homepage and category pages"""
    print("4. Testing Homepage/Category Scraping...")
    
    base_urls = [
        "https://www.illawarramercury.com.au",
        "https://www.illawarramercury.com.au/news/",
        "https://www.illawarramercury.com.au/sport/"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_urls = []
    
    for url in base_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all story links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/story/' in href:
                    full_url = urljoin("https://www.illawarramercury.com.au", href)
                    if full_url not in all_urls:
                        all_urls.append(full_url)
        
        except Exception as e:
            print(f"   Failed to scrape {url}: {e}")
    
    # Filter by query relevance (simple keyword matching)
    relevant_urls = []
    query_words = query.lower().split()
    
    for url in all_urls:
        url_text = url.lower()
        if any(word in url_text for word in query_words):
            relevant_urls.append(url)
    
    print(f"   Found {len(relevant_urls)} relevant articles from homepage scraping")
    return relevant_urls[:10]

def test_article_extraction(url):
    """Test article content extraction from a URL"""
    print(f"\n=== Testing Article Extraction ===")
    print(f"URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract title
        title_selectors = [
            'h1',
            '.story-title',
            '.article-title',
            'title'
        ]
        
        title = "No title found"
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # Extract content with multiple strategies
        content_selectors = [
            '.story-body',
            '.article-body',
            '.content',
            'div[data-module="ArticleBody"]',
            '.Paragraph_wrapper__6w7GG',
            'div.mx-auto.mb-6.px-4 p'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = '\n'.join([elem.get_text().strip() for elem in elements if elem.get_text().strip()])
                if len(content) > 100:  # Only use if we got substantial content
                    break
        
        # If no content found, try extracting all paragraphs
        if len(content) < 100:
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        # Extract author and date
        author = "Unknown author"
        date = "Unknown date"
        
        author_selectors = ['[data-testid="author-link"]', '.author', '.byline']
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text().strip()
                break
        
        print(f"Title: {title}")
        print(f"Author: {author}")
        print(f"Date: {date}")
        print(f"Content length: {len(content)} characters")
        print(f"Content preview: {content[:200]}...")
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'content': content,
            'url': url
        }
        
    except Exception as e:
        print(f"Failed to extract content: {e}")
        return None

if __name__ == "__main__":
    # Test search strategies
    results = test_search_strategies("shellharbour council")
    
    # If we found results, test article extraction on the first one
    if results:
        print(f"\n" + "="*50)
        test_article_extraction(results[0])
    else:
        print("\nNo articles found to test extraction on.")
    
    print(f"\n" + "="*50)
    print("Testing complete!")
