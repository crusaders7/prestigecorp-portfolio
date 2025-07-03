# api/download.py
from http.server import BaseHTTPRequestHandler
import json
import io
import zipfile
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            articles = data.get('articles', [])
            format_type = data.get('format', 'json')
            
            if not articles:
                self.send_error_response(400, 'No articles to download')
                return
            
            if format_type == 'json':
                # Return JSON file
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Disposition', 
                    f'attachment; filename="newspaper_articles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                json_data = json.dumps(articles, indent=2, ensure_ascii=False)
                self.wfile.write(json_data.encode('utf-8'))
                
            elif format_type == 'zip':
                # Create ZIP with individual text files
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add JSON file
                    json_data = json.dumps(articles, indent=2, ensure_ascii=False)
                    zip_file.writestr('all_articles.json', json_data)
                    
                    # Add individual text files
                    for article in articles:
                        # Safe filename
                        title_safe = article['title'][:50].replace('/', '-').replace('\\', '-')
                        filename = f"{article['id']}_{title_safe}.txt"
                        
                        content = f"Title: {article['title']}\n"
                        content += f"URL: {article['url']}\n"
                        content += f"Date: {article.get('date', 'Unknown')}\n"
                        content += f"Scraped: {article['scraped_at']}\n"
                        content += f"\n{'-'*50}\n\n"
                        content += article['content']
                        
                        zip_file.writestr(filename, content.encode('utf-8'))
                
                # Send ZIP file
                self.send_response(200)
                self.send_header('Content-type', 'application/zip')
                self.send_header('Content-Disposition', 
                    f'attachment; filename="newspaper_articles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                zip_buffer.seek(0)
                self.wfile.write(zip_buffer.read())
            
            else:
                self.send_error_response(400, 'Invalid format specified')
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
