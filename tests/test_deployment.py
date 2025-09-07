import requests
import json

def test_deployment():
    urls = [
        'https://fresh-news-deployment-1o1510p8e-prestigecorp4s-projects.vercel.app/',
        'https://fresh-news-deployment-prestigecorp4s-projects.vercel.app/',
        'https://news.prestigecorp.au/'
    ]
    
    for url in urls:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            if response.status_code == 200:
                print("✅ SUCCESS - Application is working!")
                print(f"Content length: {len(response.text)}")
                if response.text:
                    print(f"First 200 chars: {response.text[:200]}")
            else:
                print(f"❌ ERROR - Status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_deployment()