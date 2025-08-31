#!/usr/bin/env python3
"""
Vercel Deployment Diagnostics
Check for common deployment issues
"""
import os
import json

def check_deployment_issues():
    print('🔍 Vercel Deployment Diagnostics')
    print('=' * 50)
    
    # Check 1: Python imports and dependencies
    print('1. Checking Python imports...')
    try:
        import requests
        print('   ✅ requests module available')
    except ImportError:
        print('   ❌ requests module missing - this could cause deployment failure')
    
    try:
        import json
        print('   ✅ json module available')
    except ImportError:
        print('   ❌ json module missing')
    
    # Check 2: File structure
    print('\n2. Checking file structure...')
    api_files = [
        'search.py',
        'debug.py',
        'protected_cse.py',
        'protection_config.json'
    ]
    
    for file in api_files:
        if os.path.exists(file):
            print(f'   ✅ {file} found')
        else:
            print(f'   ❌ {file} missing')
    
    # Check 3: Configuration files
    print('\n3. Checking configuration...')
    config_files = [
        '../vercel.json',
        '../requirements.txt',
        'protection_config.json'
    ]
    
    for file in config_files:
        if os.path.exists(file):
            print(f'   ✅ {file} found')
            if file.endswith('.json'):
                try:
                    with open(file, 'r') as f:
                        json.load(f)
                    print(f'      ✅ {file} is valid JSON')
                except:
                    print(f'      ❌ {file} has invalid JSON')
        else:
            print(f'   ❌ {file} missing')
    
    # Check 4: Search.py syntax
    print('\n4. Checking search.py syntax...')
    try:
        with open('search.py', 'r') as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, 'search.py', 'exec')
        print('   ✅ search.py syntax is valid')
        
        # Check for required imports
        if 'import requests' in content:
            print('   ✅ requests import found')
        else:
            print('   ❌ requests import missing')
            
        if 'class handler' in content:
            print('   ✅ handler class found')
        else:
            print('   ❌ handler class missing')
            
    except Exception as e:
        print(f'   ❌ search.py error: {e}')
    
    # Check 5: API key security
    print('\n5. Checking API key...')
    try:
        with open('search.py', 'r') as f:
            content = f.read()
        
        if 'AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0' in content:
            print('   ✅ Google CSE API key found in code')
        else:
            print('   ❌ API key not found - this could cause runtime failures')
    except:
        print('   ❌ Could not check API key')

if __name__ == '__main__':
    check_deployment_issues()
