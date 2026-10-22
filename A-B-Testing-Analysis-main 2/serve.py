#!/usr/bin/env python3
"""
Simple HTTP Server for A/B Testing Analysis Studio Website
Run: python3 serve.py
"""
import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    port = PORT
    # Try preferred ports if 8080 is occupied
    for candidate_port in [8080, 8000, 8888, 5000, 3000]:
        try:
            with socketserver.TCPServer(("", candidate_port), Handler) as httpd:
                print(f"\n========================================================")
                print(f"  A/B Testing Analysis Studio Website")
                print(f"  Theme: Deep Blue & Black")
                print(f"  Serving locally at: http://localhost:{candidate_port}")
                print(f"  Directory: {DIRECTORY}")
                print(f"  Press Ctrl+C to stop.")
                print(f"========================================================\n")
                httpd.serve_forever()
        except OSError as e:
            if "Address already in use" in str(e):
                continue
            else:
                raise e

if __name__ == "__main__":
    run()
