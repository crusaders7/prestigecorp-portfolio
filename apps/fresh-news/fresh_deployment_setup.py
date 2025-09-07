#!/usr/bin/env python3
"""
Clean Deployment Setup - All files ready for fresh Vercel project
"""

import os
import shutil

print("🚀 CLEAN DEPLOYMENT SETUP")
print("="*50)

# Create a clean deployment directory
deploy_dir = "fresh-news-deployment"
if os.path.exists(deploy_dir):
    shutil.rmtree(deploy_dir)

os.makedirs(deploy_dir)
os.makedirs(f"{deploy_dir}/api")

print(f"✅ Created clean directory: {deploy_dir}")

# Copy the working files
files_to_copy = [
    ("projects/newspaperscraper/api/search.py", f"{deploy_dir}/api/search.py"),
    ("projects/newspaperscraper/api/protected_cse.py", f"{deploy_dir}/api/protected_cse.py"),
    ("projects/newspaperscraper/index.html", f"{deploy_dir}/index.html"),
    ("projects/newspaperscraper/requirements.txt", f"{deploy_dir}/requirements.txt"),
]

for src, dst in files_to_copy:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"✅ Copied: {src} → {dst}")
    else:
        print(f"❌ Missing: {src}")

# Create perfect vercel.json
vercel_config = """{
  "version": 2,
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "functions": {
    "api/*.py": {
      "runtime": "python3.8"
    }
  },
  "env": {
    "GOOGLE_API_KEY": "@google_api_key",
    "GOOGLE_CSE_ID": "@google_cse_id"
  }
}"""

with open(f"{deploy_dir}/vercel.json", "w") as f:
    f.write(vercel_config)

print(f"✅ Created: {deploy_dir}/vercel.json")

print(f"\n🎯 READY FOR DEPLOYMENT!")
print(f"📁 All files are in: {deploy_dir}/")
print(f"\n📋 NEXT STEPS:")
print(f"1. Delete old Vercel project")
print(f"2. Create new Vercel project")
print(f"3. Point to this repository")
print(f"4. Set Root Directory to: {deploy_dir}")
print(f"5. Add environment variables")
print(f"6. Deploy!")

print(f"\n🔑 ENVIRONMENT VARIABLES:")
print(f"GOOGLE_API_KEY = AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0")
print(f"GOOGLE_CSE_ID = 012527284968046999840:zzi3qgsoibq")

print("\n" + "="*50)
