#!/usr/bin/env python3
"""
Check Vercel diagnostic endpoint
"""

import requests
import json

def check_diagnostic():
    print('🔍 Vercel Diagnostic Check')
    print('=' * 40)
    
    try:
        response = requests.get('https://news.prestigecorp.au/api/debug', timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Diagnostic endpoint working!')
            print()
            
            # Key diagnostic info
            print(f'Search.py exists: {data.get("search_py_exists", "unknown")}')
            print(f'Contains Google CSE: {data.get("search_py_contains_google_cse", "unknown")}')
            print(f'File size: {data.get("search_py_size", "unknown")} chars')
            print(f'Requests available: {data.get("requests_available", "unknown")}')
            
            # Show first 100 chars of search.py
            first_100 = data.get('search_py_first_100_chars', '')
            if first_100:
                print(f'\nFirst 100 chars of search.py:')
                print(f'"{first_100}"')
            
            # Show file listing
            files = data.get('file_listing', [])
            print(f'\nFiles in deployment: {len(files)} files')
            print(f'Sample files: {files[:10]}')
            
            # Check environment
            env = data.get('environment', {})
            print(f'\nVercel environment variables count: {len(env)}')
            
        else:
            print(f'❌ Diagnostic failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    check_diagnostic()
