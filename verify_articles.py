import requests
from bs4 import BeautifulSoup

urls = [
    'https://www.illawarramercury.com.au/story/9046400/heavy-rain-causes-brown-sediment-in-shellharbour-marina/',
    'https://www.illawarramercury.com.au/story/8279850/wollongong-council-to-erect-80k-sculpture-to-honour-uci-championships/'
]

print('Verifying found articles:')
print('='*50)

for i, url in enumerate(urls, 1):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')
            title = soup.find('h1')
            title_text = title.get_text().strip() if title else 'No title found'
            
            # Check for shellharbour council mentions
            content = resp.text.lower()
            shellharbour_count = content.count('shellharbour')
            council_count = content.count('council')
            
            print(f'{i}. TITLE: {title_text}')
            print(f'   URL: {url}')
            print(f'   Mentions: shellharbour({shellharbour_count}), council({council_count})')
            
            if shellharbour_count > 0 and council_count > 0:
                status = "✓ RELEVANT"
            elif shellharbour_count > 0 or council_count > 0:
                status = "? PARTIAL"
            else:
                status = "✗ NOT RELEVANT"
                
            print(f'   Status: {status}')
            print()
        else:
            print(f'{i}. ERROR: HTTP {resp.status_code} for {url}')
            
    except Exception as e:
        print(f'{i}. ERROR: {e} for {url}')
