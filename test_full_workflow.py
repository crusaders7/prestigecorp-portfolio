import requests
import json

def test_full_workflow():
    base_url = "https://fresh-news-deployment-prestigecorp4s-projects.vercel.app/api"
    
    print("🔍 Testing full search and scrape workflow...")
    
    # Step 1: Search for articles
    search_url = f"{base_url}/search"
    search_data = {
        "query": "climate change",
        "num_results": 3
    }
    
    try:
        print(f"\n1️⃣ Searching for articles...")
        search_response = requests.post(
            search_url,
            headers={'Content-Type': 'application/json'},
            json=search_data,
            timeout=15
        )
        
        print(f"Search Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            search_results = search_response.json()
            urls = search_results.get('urls', [])
            print(f"✅ Found {len(urls)} URLs to scrape")
            
            if urls:
                # Show first few URLs
                for i, url in enumerate(urls[:3], 1):
                    print(f"   {i}. {url}")
                
                # Step 2: Scrape the articles
                print(f"\n2️⃣ Scraping articles...")
                scrape_url = f"{base_url}/scrape"
                scrape_data = {"urls": urls[:2]}  # Scrape first 2 articles
                
                scrape_response = requests.post(
                    scrape_url,
                    headers={'Content-Type': 'application/json'},
                    json=scrape_data,
                    timeout=30
                )
                
                print(f"Scrape Status: {scrape_response.status_code}")
                
                if scrape_response.status_code == 200:
                    scrape_results = scrape_response.json()
                    articles = scrape_results.get('articles', [])
                    
                    print(f"✅ Successfully scraped {len(articles)} articles")
                    
                    for i, article in enumerate(articles, 1):
                        print(f"\n📰 Article {i}:")
                        print(f"   Title: {article.get('title', 'No title')}")
                        print(f"   Date: {article.get('date', 'No date')}")
                        content = article.get('content', '')
                        print(f"   Content Length: {len(content)} characters")
                        
                        if len(content) > 1000:
                            print(f"   ✅ FULL ARTICLE CAPTURED!")
                            print(f"   Preview: {content[:300]}...")
                        elif len(content) > 200:
                            print(f"   ⚠️ Partial content: {content[:200]}...")
                        else:
                            print(f"   ❌ Minimal content: {content}")
                            
                    errors = scrape_results.get('errors', [])
                    if errors:
                        print(f"\n⚠️ Some scraping errors:")
                        for error in errors:
                            print(f"   - {error.get('url', 'Unknown')}: {error.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Scraping failed: {scrape_response.text[:200]}")
            else:
                print("❌ No URLs found in search results")
        else:
            print(f"❌ Search failed: {search_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_full_workflow()