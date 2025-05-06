#!/usr/bin/env python3
"""
Script to start both the HTTP server and the API server.
"""

import os
import sys
import subprocess
import time
import argparse
import threading
import http.server
import socketserver

def start_http_server(port):
    """Start the HTTP server."""
    print(f"Starting HTTP server on port {port}...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    print(f"HTTP server running at http://localhost:{port}")
    httpd.serve_forever()

def start_api_server(port, supabase_key=None):
    """Start the API server."""
    print(f"Starting API server on port {port}...")
    
    cmd = [sys.executable, "run_api_server.py", "--port", str(port)]
    if supabase_key:
        cmd.extend(["--supabase-key", supabase_key])
    
    # Use subprocess.Popen to run the API server in the background
    process = subprocess.Popen(cmd)
    
    # Wait a moment to make sure the server starts
    time.sleep(1)
    
    print(f"API server running at http://localhost:{port}")
    return process

def main():
    """Main function to start both servers."""
    parser = argparse.ArgumentParser(description='Start both HTTP and API servers.')
    parser.add_argument('--http-port', type=int, default=8000, help='Port for the HTTP server')
    parser.add_argument('--api-port', type=int, default=8080, help='Port for the API server')
    parser.add_argument('--supabase-key', type=str, help='Supabase service key')
    
    args = parser.parse_args()
    
    # Start the API server in a separate process
    api_process = start_api_server(args.api_port, args.supabase_key)
    
    try:
        # Start the HTTP server in the main thread
        http_thread = threading.Thread(target=start_http_server, args=(args.http_port,))
        http_thread.daemon = True
        http_thread.start()
        
        print(f"\nServers are running:")
        print(f"- Website: http://localhost:{args.http_port}")
        print(f"- API: http://localhost:{args.api_port}")
        print("\nPress Ctrl+C to stop both servers.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping servers...")
        api_process.terminate()
        print("Servers stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
