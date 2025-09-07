#!/usr/bin/env python3
"""
Debug endpoint for Vercel deployment
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to debug endpoint"""
        
        try:
            # Debug information
            debug_info = {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "GOOGLE_API_KEY": "Present" if os.environ.get("GOOGLE_API_KEY") else "Missing",
                    "GOOGLE_CSE_ID": "Present" if os.environ.get("GOOGLE_CSE_ID") else "Missing"
                },
                "message": "Google CSE API Debug Endpoint",
                "endpoints": {
                    "/api/search": "Main search endpoint (POST)",
                    "/api/debug": "This debug endpoint (GET)",
                    "/api/test": "Test endpoint (GET)",
                    "/api/minimal": "Minimal test endpoint (GET)"
                }
            }
            
            # Set response headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send response
            response = json.dumps(debug_info, indent=2)
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
