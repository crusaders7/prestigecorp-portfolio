from http.server import BaseHTTPRequestHandler
import json
import sys
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simple test response
        response = {
            'status': 'success',
            'message': 'Vercel deployment is working!',
            'python_version': sys.version,
            'environment': 'vercel',
            'timestamp': '2025-08-31',
            'test_imports': self.test_imports()
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def test_imports(self):
        """Test if required modules can be imported"""
        results = {}
        
        try:
            import requests
            results['requests'] = 'OK'
        except ImportError as e:
            results['requests'] = f'FAILED: {str(e)}'
        
        try:
            import json
            results['json'] = 'OK'
        except ImportError as e:
            results['json'] = f'FAILED: {str(e)}'
            
        try:
            import os
            results['os'] = 'OK'
        except ImportError as e:
            results['os'] = f'FAILED: {str(e)}'
            
        return results
