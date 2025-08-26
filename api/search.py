from http.server import BaseHTTPRequestHandler
import json

# Test if basic imports work
try:
    import requests
    import_requests_ok = True
    requests_error = None
except ImportError as e:
    import_requests_ok = False
    requests_error = str(e)

try:
    from bs4 import BeautifulSoup
    import_bs4_ok = True
    bs4_error = None
except ImportError as e:
    import_bs4_ok = False
    bs4_error = str(e)

try:
    from urllib.parse import quote_plus, urljoin
    import_urllib_ok = True
    urllib_error = None
except ImportError as e:
    import_urllib_ok = False
    urllib_error = str(e)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            print("Search function called!")
            
            # Check import status
            if not import_requests_ok:
                self.send_error_response(500, f'Requests import failed: {requests_error}')
                return
            if not import_bs4_ok:
                self.send_error_response(500, f'BeautifulSoup import failed: {bs4_error}')
                return
            if not import_urllib_ok:
                self.send_error_response(500, f'urllib.parse import failed: {urllib_error}')
                return
                
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, 'No data received')
                return
                
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error_response(400, f'Invalid JSON data: {str(e)}')
                return

            query = data.get('query', '').strip()

            if not query:
                self.send_error_response(400, 'Please enter a search term')
                return

            # For now, return a test response
            print(f"Received query: {query}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'query': query,
                'found': 0,
                'urls': [],
                'sources_searched': ['test'],
                'debug': {
                    'imports_ok': {
                        'requests': import_requests_ok,
                        'beautifulsoup4': import_bs4_ok,
                        'urllib': import_urllib_ok
                    },
                    'message': 'Test response - basic function working'
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Unexpected error in do_POST: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            self.send_error_response(500, f'Internal server error: {str(e)}')

    def send_error_response(self, code, message):
        try:
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'error': message}
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            print(f"Failed to send error response: {e}")
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Internal server error')
            except:
                print(f"Critical error - unable to send any response: {message}")