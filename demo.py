#!/usr/bin/env python3
"""
Simple HTTP server to serve files from current directory
"""
import http.server
import socketserver
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with better logging"""
    
    def log_message(self, format, *args):
        """Override to use timestamp and log to stdout"""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")
    
    def end_headers(self):
        """Add CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        address = f"http://localhost:{PORT}"
        print(f"Server started at {address}")
        print(f"Serving directory: {os.getcwd()}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()

