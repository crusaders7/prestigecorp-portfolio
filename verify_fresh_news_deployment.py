#!/usr/bin/env python3
"""
Deployment Verification Script for Fresh-News Application
"""

import os
import json

def verify_deployment_structure():
    """Verify the deployment directory structure"""
    print("🔍 Verifying deployment structure...")
    
    # Check if the main deployment directory exists
    if not os.path.exists("fresh-news-deployment"):
        print("❌ fresh-news-deployment directory not found")
        return False
    
    print("✅ fresh-news-deployment directory found")
    
    # Check required files in the deployment directory
    required_files = [
        "fresh-news-deployment/index.html",
        "fresh-news-deployment/vercel.json",
        "fresh-news-deployment/requirements.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} found")
        else:
            print(f"❌ {os.path.basename(file_path)} missing")
            return False
    
    # Check API directory and files
    if not os.path.exists("fresh-news-deployment/api"):
        print("❌ api directory not found")
        return False
    
    print("✅ api directory found")
    
    required_api_files = [
        "fresh-news-deployment/api/search.py",
        "fresh-news-deployment/api/scrape.py",
        "fresh-news-deployment/api/download.py"
    ]
    
    for file_path in required_api_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} found")
        else:
            print(f"❌ {os.path.basename(file_path)} missing")
            return False
    
    return True

def verify_vercel_config():
    """Verify Vercel configuration"""
    print("\n🔍 Verifying Vercel configuration...")
    
    try:
        with open("fresh-news-deployment/vercel.json", "r") as f:
            config = json.load(f)
        
        # Check required configuration elements
        required_keys = ["version", "builds", "routes", "functions"]
        for key in required_keys:
            if key in config:
                print(f"✅ {key} configured")
            else:
                print(f"❌ {key} missing")
                return False
        
        # Check builds configuration
        builds = config.get("builds", [])
        if any(build.get("src") == "api/*.py" for build in builds):
            print("✅ API build configuration correct")
        else:
            print("❌ API build configuration incorrect")
            return False
        
        # Check routes configuration
        routes = config.get("routes", [])
        api_route = any(route.get("src", "").startswith("/api/") for route in routes)
        index_route = any(route.get("src", "").startswith("/(.*)") for route in routes)
        
        if api_route and index_route:
            print("✅ Routes configuration correct")
        else:
            print("❌ Routes configuration incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Vercel configuration verification failed: {e}")
        return False

def verify_dependencies():
    """Verify dependencies"""
    print("\n🔍 Verifying dependencies...")
    
    try:
        with open("fresh-news-deployment/requirements.txt", "r") as f:
            content = f.read()
        
        required_deps = ["requests", "google-api-python-client", "beautifulsoup4", "lxml"]
        for dep in required_deps:
            if dep in content:
                print(f"✅ {dep} dependency found")
            else:
                print(f"❌ {dep} dependency missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Dependencies verification failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Fresh-News Deployment Verification")
    print("=" * 40)
    
    checks = [
        ("Deployment Structure", verify_deployment_structure),
        ("Vercel Configuration", verify_vercel_config),
        ("Dependencies", verify_dependencies)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        if check_func():
            passed += 1
            print(f"✅ {check_name} verification passed")
        else:
            print(f"❌ {check_name} verification failed")
        print()
    
    print("=" * 40)
    print(f"Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All verifications passed!")
        print("\n✅ Your fresh-news-deployment is ready for Vercel deployment.")
        print("\nNext steps:")
        print("1. Commit and push the changes to your repository")
        print("2. Vercel should automatically detect the fresh-news-deployment directory")
        print("3. Make sure to set the required environment variables in Vercel:")
        print("   - GOOGLE_API_KEY")
        print("   - GOOGLE_CSE_ID")
        return True
    else:
        print("❌ Some verifications failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    main()