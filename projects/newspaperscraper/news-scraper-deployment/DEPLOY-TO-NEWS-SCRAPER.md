# Deploy Google CSE to news-scraper-vercel Project

## Quick Deployment Steps

Your Google CSE code is ready to deploy to your existing `news-scraper-vercel` project that already has the `news.prestigecorp.au` domain configured.

### Option 1: GitHub Repository Update (Recommended)

1. **Find your news-scraper repository on GitHub:**
   - Go to https://github.com/prestigecorp4-5361 (or your GitHub account)
   - Look for a repository named `news-scraper-vercel` or similar

2. **Replace the repository contents:**
   - Upload all files from `C:\Users\prest\prestigecorp-portfolio\news-scraper-deployment\` to your news-scraper repository
   - Make sure to include:
     - `api/` folder with all Python files
     - `vercel.json` 
     - `requirements.txt`
     - `index.html`

3. **Set Environment Variables in Vercel:**
   - Go to your Vercel dashboard → news-scraper-vercel project → Settings → Environment Variables
   - Add these variables:
     ```
     GOOGLE_API_KEY = AIzaSyDUfCvNOnT7K6GC5_9fLe6yE-p5pQys9N0
     GOOGLE_CSE_ID = 012527284968046999840:zzi3qgsoibq
     ```

4. **Trigger Deployment:**
   - Push changes to your repository
   - Vercel will automatically deploy
   - Your API will be available at: `https://news.prestigecorp.au/api/search`

### Option 2: Vercel CLI Deployment

If you have Vercel CLI installed:

```bash
cd C:\Users\prest\prestigecorp-portfolio\news-scraper-deployment
vercel --prod
```

### Option 3: Connect Different Repository

In your Vercel dashboard:
1. Go to news-scraper-vercel project settings
2. Change the Git repository to point to `crusaders7/prestigecorp-portfolio`
3. Set the Root Directory to `/` (or leave blank)
4. Add the environment variables above

## Testing After Deployment

Once deployed, test your API:

```bash
curl -X POST https://news.prestigecorp.au/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "shellharbour council", "sources": ["illawarra_mercury"]}'
```

## Your Working Domain

After deployment, your Google CSE API will be available at:
- **Main domain:** https://news.prestigecorp.au
- **API endpoint:** https://news.prestigecorp.au/api/search
- **Debug endpoint:** https://news.prestigecorp.au/api/debug
- **Test endpoint:** https://news.prestigecorp.au/api/test

## Files Included in Deployment Package

✅ `api/search.py` - Main Google CSE search API
✅ `api/protected_cse.py` - Protection and rate limiting
✅ `api/debug.py` - Debug endpoint
✅ `api/test.py` - Test endpoint  
✅ `api/minimal.py` - Minimal test endpoint
✅ `vercel.json` - Vercel configuration
✅ `requirements.txt` - Python dependencies
✅ `index.html` - Frontend interface

All your Google CSE code with the working API key and protection system is ready to deploy!
