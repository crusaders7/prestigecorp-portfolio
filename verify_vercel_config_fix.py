#!/usr/bin/env python3
"""
Verification Script for Vercel Configuration Fix
"""

import json
import os

def verify_vercel_config():
    """Verify the Vercel configuration fix"""
    print("🔍 Verifying Vercel configuration fix...")
    
    try:
        # Read the vercel.json file
        with open("fresh-news-deployment/vercel.json", "r") as f:
            config = json.load(f)
        
        # Check that the configuration has the correct structure
        print("✅ vercel.json file loaded successfully")
        
        # Verify that 'builds' property is not present
        if 'builds' in config:
            print("❌ Error: 'builds' property should not be present")
            return False
        else:
            print("✅ 'builds' property correctly removed")
        
        # Verify that 'functions' property is present
        if 'functions' in config:
            print("✅ 'functions' property correctly present")
            
            # Check functions configuration
            functions = config['functions']
            if 'api/*.py' in functions:
                print("✅ API functions configuration present")
                
                # Check runtime
                api_config = functions['api/*.py']
                if 'runtime' in api_config and api_config['runtime'] == 'python3.9':
                    print("✅ Python 3.9 runtime correctly configured")
                else:
                    print("❌ Error: Python 3.9 runtime not correctly configured")
                    return False
            else:
                print("❌ Error: API functions configuration missing")
                return False
        else:
            print("❌ Error: 'functions' property missing")
            return False
        
        # Verify other required properties
        required_properties = ['version', 'routes', 'env']
        for prop in required_properties:
            if prop in config:
                print(f"✅ {prop} property present")
            else:
                print(f"❌ Error: {prop} property missing")
                return False
        
        # Verify routes configuration
        routes = config['routes']
        if len(routes) >= 2:
            print("✅ Routes configuration present")
            
            # Check for API route
            api_route = any(route.get('src', '').startswith('/api/') for route in routes)
            if api_route:
                print("✅ API route correctly configured")
            else:
                print("❌ Error: API route not correctly configured")
                return False
            
            # Check for index.html route
            index_route = any(route.get('src', '') == '/(.*)' for route in routes)
            if index_route:
                print("✅ Index route correctly configured")
            else:
                print("❌ Error: Index route not correctly configured")
                return False
        else:
            print("❌ Error: Routes configuration incomplete")
            return False
        
        # Verify environment variables
        env = config['env']
        required_env_vars = ['GOOGLE_API_KEY', 'GOOGLE_CSE_ID']
        for var in required_env_vars:
            if var in env:
                print(f"✅ {var} environment variable present")
            else:
                print(f"❌ Error: {var} environment variable missing")
                return False
        
        print("\n🎉 Vercel configuration fix verification PASSED")
        print("\nSummary of fixes:")
        print("- Removed conflicting 'builds' property")
        print("- Kept 'functions' property for advanced features")
        print("- Maintained all other required configurations")
        print("- Preserved environment variables")
        
        return True
        
    except Exception as e:
        print(f"❌ Vercel configuration verification failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🔧 Vercel Configuration Fix Verification")
    print("=" * 40)
    
    if verify_vercel_config():
        print("\n✅ Vercel configuration is now correctly set up!")
        print("\nNext steps:")
        print("1. Commit and push the changes to your repository")
        print("2. The deployment should now proceed without the 'Conflicting functions and builds configuration' error")
        print("3. Monitor the deployment logs to ensure everything works correctly")
        return True
    else:
        print("\n❌ Vercel configuration still has issues that need to be addressed")
        return False

if __name__ == "__main__":
    main()