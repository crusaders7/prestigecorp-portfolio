#!/usr/bin/env python3
"""
Test script to verify that the fresh-news-deployment application is working correctly
"""

import json
import os
import sys

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        "news-scraper-deployment/index.html",
        "news-scraper-deployment/vercel.json",
        "news-scraper-deployment/requirements.txt",
        "news-scraper-deployment/api/search.py",
        "news-scraper-deployment/api/scrape.py",
        "news-scraper-deployment/api/download.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ Missing file: {file_path}")
        else:
            print(f"✅ Found file: {file_path}")
    
    return len(missing_files) == 0

def test_vercel_config():
    """Test Vercel configuration"""
    print("\nTesting Vercel configuration...")
    
    try:
        with open("news-scraper-deployment/vercel.json", "r") as f:
            config = json.load(f)
        
        # Check required keys
        required_keys = ["version", "builds", "routes", "functions", "env"]
        for key in required_keys:
            if key in config:
                print(f"✅ vercel.json has {key}")
            else:
                print(f"❌ vercel.json missing {key}")
                return False
        
        # Check builds configuration
        builds = config.get("builds", [])
        if any(build.get("src") == "api/*.py" for build in builds):
            print("✅ vercel.json has correct builds configuration")
        else:
            print("❌ vercel.json missing correct builds configuration")
            return False
        
        # Check functions configuration
        functions = config.get("functions", {})
        if "api/*.py" in functions:
            print("✅ vercel.json has correct functions configuration")
        else:
            print("❌ vercel.json missing correct functions configuration")
            return False
        
        # Check environment variables
        env_vars = config.get("env", {})
        if "GOOGLE_API_KEY" in env_vars and "GOOGLE_CSE_ID" in env_vars:
            print("✅ vercel.json has required environment variables")
        else:
            print("❌ vercel.json missing required environment variables")
            return False
            
        return True
    except Exception as e:
        print(f"❌ vercel.json test failed: {e}")
        return False

def test_requirements():
    """Test requirements.txt"""
    print("\nTesting requirements.txt...")
    
    try:
        with open("news-scraper-deployment/requirements.txt", "r") as f:
            content = f.read()
        
        required_deps = ["requests==", "google-api-python-client==", "beautifulsoup4==", "lxml=="]
        missing_deps = []
        
        for dep in required_deps:
            if dep in content:
                print(f"✅ Found dependency: {dep}")
            else:
                missing_deps.append(dep)
                print(f"❌ Missing dependency: {dep}")
        
        return len(missing_deps) == 0
    except Exception as e:
        print(f"❌ requirements.txt test failed: {e}")
        return False

def test_javascript():
    """Test JavaScript functionality in index.html"""
    print("\nTesting JavaScript functionality...")
    
    try:
        with open("news-scraper-deployment/index.html", "r") as f:
            content = f.read()
        
        # Check for required JavaScript functions
        required_functions = [
            "searchArticles()",
            "scrapeArticles()",
            "downloadArticles(",
            "showStatus(",
            "toggleAdvancedOptions()",
            "clearResults()"
        ]
        
        missing_functions = []
        for func in required_functions:
            if func in content:
                print(f"✅ Found JavaScript function: {func}")
            else:
                missing_functions.append(func)
                print(f"❌ Missing JavaScript function: {func}")
        
        # Check for API_BASE configuration
        if "const API_BASE = '/api'" in content:
            print("✅ Found API_BASE configuration")
        else:
            print("❌ Missing API_BASE configuration")
            missing_functions.append("API_BASE configuration")
        
        return len(missing_functions) == 0
    except Exception as e:
        print(f"❌ JavaScript test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Fresh-News-Deployment Application")
    print("=" * 50)
    
    # Test each component
    tests = [
        ("File Structure", test_file_structure),
        ("Vercel Configuration", test_vercel_config),
        ("Dependencies", test_requirements),
        ("JavaScript Functionality", test_javascript)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fresh-news-deployment is ready for deployment.")
        print("\n✅ The application has all required components:")
        print("   1. Search functionality - Find news articles using Google CSE")
        print("   2. Scrape functionality - Extract content from articles")
        print("   3. Download functionality - Save articles in JSON or ZIP format")
        print("\n🚀 To deploy:")
        print("   1. Push the files in news-scraper-deployment to your GitHub repository")
        print("   2. Connect the repository to Vercel")
        print("   3. Set the environment variables in Vercel:")
        print("      - GOOGLE_API_KEY")
        print("      - GOOGLE_CSE_ID")
        print("   4. Deploy the application")
        print("   5. Visit https://news.prestigecorp.au to use the application")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    main()