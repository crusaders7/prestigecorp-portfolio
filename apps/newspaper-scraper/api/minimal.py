#!/usr/bin/env python3
"""
Minimal endpoint for Vercel deployment testing
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to minimal endpoint"""
        
        # Simple response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"status": "ok", "message": "Minimal endpoint working"}
        self.wfile.write(json.dumps(response).encode())
