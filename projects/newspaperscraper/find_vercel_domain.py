#!/usr/bin/env python3
"""
Find the Vercel domain for prestigecorp-portfolio project
"""
import requests
import json

def check_common_vercel_domains():
    """Check common Vercel domain patterns"""
    
    # Common patterns for Vercel domains
    possible_domains = [
        "prestigecorp-portfolio.vercel.app",
        "prestigecorp-portfolio-git-main-crusaders7.vercel.app", 
        "prestigecorp-portfolio-crusaders7.vercel.app",
        "prestigecorp-portfolio-git-main.vercel.app"
    ]
    
    print("🔍 Checking possible Vercel domains for prestigecorp-portfolio...")
    print("=" * 60)
    
    working_domains = []
    
    for domain in possible_domains:
        try:
            print(f"Testing: https://{domain}")
            
            # Try the search endpoint
            response = requests.post(
                f"https://{domain}/api/search",
                json={"query": "test", "sources": ["illawarra_mercury"]},
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FOUND WORKING DOMAIN: https://{domain}")
                print(f"   Status: {response.status_code}")
                print(f"   Response contains: {len(data.get('articles', []))} articles")
                working_domains.append(domain)
                
            elif response.status_code == 404:
                print(f"❌ Domain exists but no /api/search endpoint")
                
            else:
                print(f"⚠️  Domain responds but unexpected status: {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"⏱️  Timeout - domain may not exist")
        except requests.exceptions.ConnectionError:
            print(f"🚫 Connection error - domain doesn't exist")
        except Exception as e:
            print(f"❓ Error: {e}")
            
        print()
    
    if working_domains:
        print("🎉 WORKING DOMAINS FOUND:")
        for domain in working_domains:
            print(f"   • https://{domain}")
            print(f"   • Test URL: https://{domain}/api/search")
        
        # Test the main page too
        print(f"\n📄 Testing main page on primary domain...")
        try:
            response = requests.get(f"https://{working_domains[0]}", timeout=10)
            if response.status_code == 200:
                print(f"✅ Main page works: https://{working_domains[0]}")
            else:
                print(f"⚠️  Main page status: {response.status_code}")
        except Exception as e:
            print(f"❓ Main page error: {e}")
            
    else:
        print("❌ No working domains found with the Google CSE API")
        print("\nYou may need to:")
        print("1. Check your Vercel dashboard for the exact domain")
        print("2. Ensure the project is deployed")
        print("3. Wait for deployment to complete")

if __name__ == "__main__":
    check_common_vercel_domains()
