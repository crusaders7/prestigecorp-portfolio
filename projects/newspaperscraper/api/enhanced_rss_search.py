
def enhanced_rss_search_illawarra_mercury(query, max_results=20):
    """
    Enhanced RSS-based search using all discovered feeds
    Includes pagination and historical feed support
    """
    import requests
    from bs4 import BeautifulSoup
    import re
    import time
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    query_terms = query.lower().split()
    all_articles = []
    
    # All discovered RSS feeds
    rss_feeds = [
        'https://www.illawarramercury.com.au/rss.xml',
        'https://www.illawarramercury.com.au/news/rss.xml',
        'https://www.illawarramercury.com.au/sport/rss.xml',
        'https://www.illawarramercury.com.au/entertainment/rss.xml',
        'https://www.illawarramercury.com.au/lifestyle/rss.xml',
    ]
    
    for feed_url in rss_feeds:
        try:
            # Try main feed
            response = requests.get(feed_url, headers=headers, timeout=15)
            if response.status_code == 200:
                articles = parse_rss_feed(response.content, query_terms, feed_url)
                all_articles.extend(articles)
            
            # Try paginated feeds
            for page in range(2, 4):  # Check pages 2-3
                paginated_url = f"{feed_url}?page={page}"
                try:
                    page_response = requests.get(paginated_url, headers=headers, timeout=10)
                    if page_response.status_code == 200:
                        page_articles = parse_rss_feed(page_response.content, query_terms, paginated_url)
                        all_articles.extend(page_articles)
                except:
                    break
            
            time.sleep(0.5)
        except Exception:
            continue
    
    # Remove duplicates and sort by relevance
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    unique_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    return unique_articles[:max_results]

def parse_rss_feed(content, query_terms, feed_url):
    """Parse RSS feed content and extract relevant articles"""
    articles = []
    
    try:
        soup = BeautifulSoup(content, 'xml')
        items = soup.find_all(['item', 'entry'])
        
        for item in items:
            article = {'feed_source': feed_url}
            
            # Extract title
            title_elem = item.find(['title'])
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
            
            # Extract URL
            link_elem = item.find(['link'])
            if link_elem:
                link = link_elem.get_text(strip=True) if link_elem.string else link_elem.get('href', '')
                article['url'] = link
            
            # Extract description
            desc_elem = item.find(['description', 'summary'])
            if desc_elem:
                article['description'] = desc_elem.get_text(strip=True)
            
            # Calculate relevance
            text_content = (
                article.get('title', '') + ' ' + 
                article.get('description', '') + ' ' + 
                article.get('url', '')
            ).lower()
            
            relevance_score = 0
            for term in query_terms:
                if term in text_content:
                    relevance_score += 1
            
            if relevance_score > 0:
                article['relevance_score'] = relevance_score
                article['source'] = 'enhanced_rss'
                articles.append(article)
    
    except Exception:
        pass
    
    return articles
