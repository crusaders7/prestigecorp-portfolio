from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Diagnostic information
            diagnostic = {
                'status': 'diagnostic_endpoint_active',
                'timestamp': '2025-08-31T01:35:00Z',
                'python_version': sys.version,
                'environment': dict(os.environ),
                'current_directory': os.getcwd(),
                'file_listing': [],
                'search_py_exists': os.path.exists('search.py'),
                'api_search_py_exists': os.path.exists('api/search.py'),
                'requests_available': False
            }
            
            # Check if we can import requests
            try:
                import requests
                diagnostic['requests_available'] = True
                diagnostic['requests_version'] = requests.__version__
            except ImportError:
                diagnostic['requests_available'] = False
            
            # List files in current directory
            try:
                diagnostic['file_listing'] = os.listdir('.')
            except:
                diagnostic['file_listing'] = ['error_listing_files']
            
            # Check for search.py content
            if os.path.exists('search.py'):
                try:
                    with open('search.py', 'r') as f:
                        content = f.read()
                        diagnostic['search_py_size'] = len(content)
                        diagnostic['search_py_contains_google_cse'] = 'google' in content.lower() and 'cse' in content.lower()
                        diagnostic['search_py_first_100_chars'] = content[:100]
                except:
                    diagnostic['search_py_error'] = 'could_not_read'
            
            self.wfile.write(json.dumps(diagnostic, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': str(e),
                'type': 'diagnostic_error'
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
