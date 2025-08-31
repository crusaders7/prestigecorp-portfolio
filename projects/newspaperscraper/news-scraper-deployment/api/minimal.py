from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'working',
            'message': 'Minimal Vercel test successful',
            'version': '2025-08-31-v2'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simple POST response
        response = {
            'status': 'post_working',
            'message': 'POST method functional',
            'test': 'minimal_deployment'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
