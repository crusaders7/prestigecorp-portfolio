# 🚀 READY TO DEPLOY: Google CSE API to news.prestigecorp.au

## ✅ EVERYTHING IS CONFIGURED!

I've just set up your deployment configuration in your GitHub repository. Here's exactly what you need to do:

## 🎯 VERCEL PROJECT SETTINGS

### Step 1: Update Your Vercel Project
1. Go to: https://vercel.com/dashboard
2. Find your **`news-scraper-vercel`** project
3. Click **Settings** → **Git**
4. Change these settings:
   - **Repository**: `crusaders7/prestigecorp-portfolio`
   - **Root Directory**: `projects/newspaperscraper`

### Step 2: Add Environment Variables
In Settings → Environment Variables, add:
```
GOOGLE_API_KEY = AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0
GOOGLE_CSE_ID = 012527284968046999840:zzi3qgsoibq
```

### Step 3: Deploy
- Save the settings (Vercel will automatically redeploy)
- Or go to **Deployments** → click **Redeploy**

## 🎉 RESULT
Your Google CSE API will be live at:
- **https://news.prestigecorp.au/api/search**
- **https://news.prestigecorp.au/api/debug**
- **https://news.prestigecorp.au/api/test**

## ✅ WHAT'S READY
- ✅ Vercel.json configured and committed
- ✅ Requirements.txt with all dependencies
- ✅ All your Google CSE code in the right place
- ✅ Protection and rate limiting included
- ✅ Same API key that works locally

## 🧪 TEST COMMAND
After deployment:
```bash
curl -X POST https://news.prestigecorp.au/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "shellharbour council", "sources": ["illawarra_mercury"]}'
```

**That's it!** Your working Google CSE system will be live on your existing domain.
