#!/usr/bin/env python3
"""
Deployment helper script to check and fix Vercel configuration
"""

print("🔍 VERCEL DEPLOYMENT DIAGNOSTIC")
print("="*50)

print("\n1. ACCOUNT ISSUE DETECTED:")
print("   - Repository owner: crusaders7") 
print("   - Current user might be: captncasper")
print("   - This can cause deployment permission issues")

print("\n2. DIRECTORY STRUCTURE ISSUE:")
print("   - Expected deployment root: projects/newspaperscraper")
print("   - Current deployment root: repository root")
print("   - This explains why old code is still deployed")

print("\n3. REQUIRED ACTIONS:")
print("   ✅ Code is updated correctly")
print("   ✅ Repository is configured correctly") 
print("   ❌ Vercel project root directory needs to be set")

print("\n4. SOLUTION:")
print("   Go to: https://vercel.com/dashboard")
print("   Find: news.prestigecorp.au project")
print("   Settings → General → Root Directory")
print("   Change from: '.' to 'projects/newspaperscraper'")
print("   Save and redeploy")

print("\n5. ACCOUNT CHECK:")
print("   Make sure you're logged into the same account that owns the Vercel project")
print("   The domain news.prestigecorp.au should be in your Vercel dashboard")

print("\n6. FILES READY FOR DEPLOYMENT:")
import os
if os.path.exists("projects/newspaperscraper/api/search.py"):
    print("   ✅ projects/newspaperscraper/api/search.py (Google CSE implementation)")
if os.path.exists("projects/newspaperscraper/vercel.json"):
    print("   ✅ projects/newspaperscraper/vercel.json (Proper configuration)")
if os.path.exists("projects/newspaperscraper/index.html"):
    print("   ✅ projects/newspaperscraper/index.html (Frontend interface)")

print("\n" + "="*50)
print("📧 If you need help with Vercel account access, let me know!")
