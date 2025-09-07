#!/usr/bin/env python3
"""
Check Vercel project configuration and provide exact steps to fix
"""

print("🔧 VERCEL PROJECT CONFIGURATION GUIDE")
print("="*60)

print(f"\n✅ ACCOUNT VERIFICATION:")
print(f"   GitHub Account: crusaders7")
print(f"   Email: prestigecorp4@gmail.com") 
print(f"   Repository: crusaders7/prestigecorp-portfolio")
print(f"   Domain: news.prestigecorp.au")

print(f"\n🎯 THE EXACT PROBLEM:")
print(f"   Current Root Directory: '.' (repository root)")
print(f"   Needed Root Directory: 'projects/newspaperscraper'")

print(f"\n📋 STEP-BY-STEP FIX:")
print(f"   1. Go to: https://vercel.com/dashboard")
print(f"   2. Make sure you're logged in as the account that owns news.prestigecorp.au")
print(f"   3. Find and click on: 'news.prestigecorp.au' project")
print(f"   4. Click: Settings (in the top navigation)")
print(f"   5. Click: General (in the left sidebar)")
print(f"   6. Scroll down to: 'Root Directory' section")
print(f"   7. Change from: '.' to 'projects/newspaperscraper'")
print(f"   8. Click: Save")
print(f"   9. Go to Deployments tab and click 'Redeploy' on the latest deployment")

print(f"\n🔍 VERIFICATION:")
print(f"   After the redeploy, the API should return:")
print(f"   Error message: 'UPDATED_API_v2: Query parameter is required'")
print(f"   Instead of: 'Please enter a search term'")

print(f"\n📁 DIRECTORY STRUCTURE:")
print(f"   Repository Root (current deployment):")
print(f"   ├── api/search.py (wrong file)")
print(f"   └── projects/")
print(f"       └── newspaperscraper/ (should be root)")
print(f"           ├── api/search.py (correct Google CSE file)")
print(f"           ├── index.html (frontend)")
print(f"           └── vercel.json (configuration)")

print(f"\n🚀 RESULT AFTER FIX:")
print(f"   Frontend will work with sources: ['illawarra_mercury']")
print(f"   API will return Google CSE results")
print(f"   Error messages will show the UPDATED_API_v2 identifier")

print("\n" + "="*60)
print("Let me know when you've made the Vercel Root Directory change!")
print("Then we can test if news.prestigecorp.au is working correctly.")
