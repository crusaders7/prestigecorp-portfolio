#!/usr/bin/env python3
"""
Test endpoint for Vercel deployment
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to test endpoint"""
        
        try:
            # Test response
            test_response = {
                "status": "ok",
                "message": "Google CSE API Test Endpoint Working",
                "test": "successful"
            }
            
            # Set response headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send response
            response = json.dumps(test_response, indent=2)
            self.wfile.write(response.encode())
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": str(e),
                "status": "error"
            }
            self.wfile.write(json.dumps(error_response).encode())
