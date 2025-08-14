from http.server import BaseHTTPRequestHandler
import json
import logging
import os
import asyncio
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple test handler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "Bot API is running",
            "timestamp": datetime.now().isoformat(),
            "method": "GET"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                logger.info(f"Received POST data: {data}")
            else:
                data = {}
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "received",
                "timestamp": datetime.now().isoformat(),
                "method": "POST",
                "data_received": bool(data)
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"Error in POST handler: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(error_response).encode())