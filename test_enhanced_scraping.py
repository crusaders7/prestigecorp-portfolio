import requests
import json

def test_enhanced_scraping():
    # Test URL - using a news site that should have substantial content
    test_urls = [
        "https://www.illawarramercury.com.au/story/8452890/shellharbour-shark-attack-leaves-man-with-leg-injuries/",
        "https://www.illawarramercury.com.au/story/8452754/bulli-womans-vision-to-turn-family-farm-into-popular-local-hangout/"
    ]
    
    api_url = "https://fresh-news-deployment-prestigecorp4s-projects.vercel.app/api/scrape"
    
    try:
        print("🕷️ Testing enhanced scraping functionality...")
        print(f"API URL: {api_url}")
        print(f"Test URLs: {test_urls}")
        
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json={'urls': test_urls},
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Scraped {data.get('scraped', 0)} articles")
            
            articles = data.get('articles', [])
            for i, article in enumerate(articles, 1):
                print(f"\n📰 Article {i}:")
                print(f"   Title: {article.get('title', 'No title')[:100]}...")
                print(f"   Date: {article.get('date', 'No date')}")
                print(f"   Content Length: {article.get('content_length', len(article.get('content', '')))} characters")
                print(f"   Content Preview: {article.get('content', 'No content')[:200]}...")
                
                # Check if we're getting full articles (not truncated)
                content = article.get('content', '')
                if len(content) > 2000:
                    print(f"   ✅ Full article captured! ({len(content)} chars)")
                elif len(content) > 500:
                    print(f"   ⚠️ Partial article captured ({len(content)} chars)")
                else:
                    print(f"   ❌ Minimal content captured ({len(content)} chars)")
            
            errors = data.get('errors', [])
            if errors:
                print(f"\n❌ Errors encountered:")
                for error in errors:
                    print(f"   - {error}")
                    
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    test_enhanced_scraping()