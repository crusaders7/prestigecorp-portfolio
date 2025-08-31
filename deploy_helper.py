#!/usr/bin/env python3
"""
Deployment Helper for news-scraper-vercel Project
Creates a zip file with all deployment files ready to upload
"""
import os
import zipfile
import shutil
from pathlib import Path

def create_deployment_zip():
    """Create a zip file with all deployment files"""
    
    deployment_dir = Path("C:/Users/prest/prestigecorp-portfolio/news-scraper-deployment")
    zip_path = Path("C:/Users/prest/prestigecorp-portfolio/news-scraper-deployment.zip")
    
    print("🚀 Creating deployment package...")
    print("=" * 50)
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from deployment directory
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                if file.endswith('.zip'):  # Skip zip files
                    continue
                    
                file_path = Path(root) / file
                arc_name = file_path.relative_to(deployment_dir)
                zipf.write(file_path, arc_name)
                print(f"✅ Added: {arc_name}")
    
    print(f"\n🎉 Deployment zip created: {zip_path}")
    print(f"📦 Size: {zip_path.stat().st_size / 1024:.1f} KB")
    
    return zip_path

def show_deployment_steps():
    """Show the deployment steps"""
    
    print("\n" + "=" * 60)
    print("🚀 DEPLOYMENT STEPS")
    print("=" * 60)
    
    print("\n1️⃣ FIND YOUR REPOSITORY:")
    print("   • Go to https://github.com/prestigecorp4-5361")
    print("   • Look for 'news-scraper-vercel' or similar repository")
    print("   • This is the repo connected to your Vercel project")
    
    print("\n2️⃣ UPLOAD FILES:")
    print("   • Download the zip file created above")
    print("   • Extract it locally")
    print("   • Upload ALL files to your GitHub repository")
    print("   • Replace existing files completely")
    
    print("\n3️⃣ SET ENVIRONMENT VARIABLES:")
    print("   • Go to https://vercel.com/dashboard")
    print("   • Find your 'news-scraper-vercel' project")
    print("   • Go to Settings → Environment Variables")
    print("   • Add these variables:")
    print("     GOOGLE_API_KEY = AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0")
    print("     GOOGLE_CSE_ID = 012527284968046999840:zzi3qgsoibq")
    
    print("\n4️⃣ DEPLOY:")
    print("   • Push changes to GitHub")
    print("   • Vercel will auto-deploy (watch the deployments tab)")
    print("   • Wait for 'Ready' status")
    
    print("\n5️⃣ TEST:")
    print("   • Visit: https://news.prestigecorp.au")
    print("   • Test API: https://news.prestigecorp.au/api/search")
    print("   • Debug endpoint: https://news.prestigecorp.au/api/debug")
    
    print("\n🎯 EXPECTED RESULT:")
    print("   Your Google CSE API working at news.prestigecorp.au!")
    print("   Same API that works locally, now live on your domain.")

if __name__ == "__main__":
    try:
        zip_path = create_deployment_zip()
        show_deployment_steps()
        
        print(f"\n📋 QUICK CHECKLIST:")
        print(f"   ✅ Deployment zip ready: {zip_path}")
        print(f"   ⏳ Upload files to GitHub repository")
        print(f"   ⏳ Set environment variables in Vercel")
        print(f"   ⏳ Wait for deployment")
        print(f"   ⏳ Test the API")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the news-scraper-deployment directory exists")
