import json
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time

def handler(event, context):
    """
    Vercel serverless function for website audit
    """
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        url = body.get('url', '').strip()
        
        if not url:
            return error_response('URL is required', 400)
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                return error_response('Invalid URL format', 400)
        except Exception:
            return error_response('Invalid URL format', 400)
        
        # Perform audit
        audit_results = perform_audit(url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(audit_results)
        }
        
    except Exception as e:
        print(f"Audit error: {str(e)}")
        return error_response(f'Audit failed: {str(e)}', 500)

def perform_audit(url):
    """
    Perform comprehensive website audit
    """
    
    results = {
        'url': url,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'overall_score': 0,
        'seo_score': 0,
        'performance_score': 0,
        'accessibility_score': 0,
        'security_score': 0,
        'pages_analyzed': 0,
        'issues_found': [],
        'recommendations': []
    }
    
    try:
        # Fetch the main page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # SEO Analysis
        seo_score = analyze_seo(soup, url)
        results['seo_score'] = seo_score
        
        # Performance Analysis  
        performance_score = analyze_performance(response, soup)
        results['performance_score'] = performance_score
        
        # Accessibility Analysis
        accessibility_score = analyze_accessibility(soup)
        results['accessibility_score'] = accessibility_score
        
        # Security Analysis
        security_score = analyze_security(response, url)
        results['security_score'] = security_score
        
        # Calculate overall score
        results['overall_score'] = round((seo_score + performance_score + accessibility_score + security_score) / 4)
        
        results['pages_analyzed'] = 1
        
        return results
        
    except requests.RequestException as e:
        results['error'] = f'Failed to fetch website: {str(e)}'
        return results
    except Exception as e:
        results['error'] = f'Analysis failed: {str(e)}'
        return results

def analyze_seo(soup, url):
    """Analyze SEO factors"""
    score = 0
    
    # Title tag
    title = soup.find('title')
    if title and title.get_text().strip():
        score += 25
        if len(title.get_text()) < 60:
            score += 10
    
    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content', '').strip():
        score += 25
    
    # H1 tag
    h1_tags = soup.find_all('h1')
    if h1_tags:
        score += 20
        if len(h1_tags) == 1:  # Exactly one H1 is ideal
            score += 10
    
    # Meta viewport
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        score += 10
    
    return min(score, 100)

def analyze_performance(response, soup):
    """Analyze performance factors"""
    score = 0
    
    # Response time (basic check)
    if hasattr(response, 'elapsed'):
        response_time = response.elapsed.total_seconds()
        if response_time < 1:
            score += 30
        elif response_time < 3:
            score += 20
        elif response_time < 5:
            score += 10
    
    # Content size
    content_size = len(response.content)
    if content_size < 100000:  # Less than 100KB
        score += 20
    elif content_size < 500000:  # Less than 500KB
        score += 15
    elif content_size < 1000000:  # Less than 1MB
        score += 10
    
    # Images with alt text
    images = soup.find_all('img')
    if images:
        images_with_alt = len([img for img in images if img.get('alt')])
        alt_ratio = images_with_alt / len(images)
        score += round(alt_ratio * 20)
    else:
        score += 10  # No images is also good for performance
    
    # CSS and JS files
    css_files = soup.find_all('link', rel='stylesheet')
    js_files = soup.find_all('script', src=True)
    
    if len(css_files) <= 3:
        score += 15
    elif len(css_files) <= 5:
        score += 10
    
    if len(js_files) <= 5:
        score += 15
    elif len(js_files) <= 10:
        score += 10
    
    return min(score, 100)

def analyze_accessibility(soup):
    """Analyze accessibility factors"""
    score = 0
    
    # Images with alt text
    images = soup.find_all('img')
    if images:
        images_with_alt = len([img for img in images if img.get('alt')])
        alt_ratio = images_with_alt / len(images)
        score += round(alt_ratio * 40)
    else:
        score += 40
    
    # Proper heading hierarchy
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if headings:
        score += 20
    
    # Form labels
    forms = soup.find_all('form')
    if forms:
        inputs = soup.find_all('input')
        labels = soup.find_all('label')
        if len(labels) >= len(inputs) * 0.8:  # 80% of inputs have labels
            score += 20
    else:
        score += 20  # No forms is neutral
    
    # Lang attribute
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        score += 20
    
    return min(score, 100)

def analyze_security(response, url):
    """Analyze security factors"""
    score = 0
    
    # HTTPS
    if url.startswith('https://'):
        score += 40
    
    # Security headers
    headers = response.headers
    
    if 'Strict-Transport-Security' in headers:
        score += 15
    
    if 'X-Content-Type-Options' in headers:
        score += 15
    
    if 'X-Frame-Options' in headers or 'Content-Security-Policy' in headers:
        score += 15
    
    if 'X-XSS-Protection' in headers:
        score += 15
    
    return min(score, 100)

def error_response(message, status_code):
    """Return standardized error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'error': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
    }