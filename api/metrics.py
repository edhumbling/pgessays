#!/usr/bin/env python3
"""
API endpoint for handling essay metrics.
This script provides a secure way to interact with Supabase without exposing API keys.
"""

import os
import json
import uuid
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import supabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration - these would be environment variables in production
SUPABASE_URL = "https://doujnhbgnzdhapehoftc.supabase.co"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SCHEMA = "paul_graham_essays"

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class MetricsHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if path == '/api/metrics/popular':
            # Get popular essays
            try:
                limit = 10
                query_params = parse_qs(parsed_url.query)
                if 'limit' in query_params:
                    limit = int(query_params['limit'][0])

                popular_essays = self.get_popular_essays(limit)
                self.wfile.write(json.dumps(popular_essays).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.wfile.write(json.dumps({"error": "Invalid endpoint"}).encode())

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/api/metrics/start':
            # Start tracking essay reading
            try:
                result = self.start_reading_tracking(data)
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == '/api/metrics/progress':
            # Update reading progress
            try:
                result = self.update_reading_progress(data)
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == '/api/metrics/complete':
            # Mark essay as completed
            try:
                result = self.mark_essay_completed(data)
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == '/api/metrics/save':
            # Save reading metrics
            try:
                result = self.save_reading_metrics(data)
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        else:
            self.wfile.write(json.dumps({"error": "Invalid endpoint"}).encode())

    def get_popular_essays(self, limit=10):
        """Get popular essays from Supabase."""
        try:
            response = supabase_client.table(f"{SCHEMA}.popular_essays") \
                .select("*") \
                .order("view_count", desc=True) \
                .limit(limit) \
                .execute()

            return response.data
        except Exception as e:
            print(f"Error getting popular essays: {e}")
            return []

    def start_reading_tracking(self, data):
        """Start tracking essay reading."""
        try:
            essay_id = data.get('essay_id')
            essay_title = data.get('essay_title')
            session_id = data.get('session_id', str(uuid.uuid4()))

            if not essay_id or not essay_title:
                return {"error": "Missing required fields"}

            # Check if we already have a record for this essay and session
            response = supabase_client.table(f"{SCHEMA}.essay_metrics") \
                .select("*") \
                .eq("essay_id", essay_id) \
                .eq("session_id", session_id) \
                .execute()

            if response.data:
                # Update existing record
                record = response.data[0]
                supabase_client.table(f"{SCHEMA}.essay_metrics") \
                    .update({"view_count": record["view_count"] + 1, "last_read": time.strftime("%Y-%m-%dT%H:%M:%SZ")}) \
                    .eq("id", record["id"]) \
                    .execute()
            else:
                # Create new record
                supabase_client.table(f"{SCHEMA}.essay_metrics") \
                    .insert({
                        "essay_id": essay_id,
                        "essay_title": essay_title,
                        "session_id": session_id,
                        "user_id": None
                    }) \
                    .execute()

            return {"success": True, "session_id": session_id}
        except Exception as e:
            print(f"Error tracking reading start: {e}")
            return {"error": str(e)}

    def update_reading_progress(self, data):
        """Update reading progress."""
        try:
            essay_id = data.get('essay_id')
            progress = data.get('progress')
            session_id = data.get('session_id')

            if not essay_id or progress is None or not session_id:
                return {"error": "Missing required fields"}

            # Get existing record
            response = supabase_client.table(f"{SCHEMA}.essay_metrics") \
                .select("*") \
                .eq("essay_id", essay_id) \
                .eq("session_id", session_id) \
                .execute()

            if response.data:
                record = response.data[0]
                # Only update if progress is higher than before
                if progress > record["max_progress"]:
                    supabase_client.table(f"{SCHEMA}.essay_metrics") \
                        .update({"max_progress": progress}) \
                        .eq("id", record["id"]) \
                        .execute()

            return {"success": True}
        except Exception as e:
            print(f"Error updating reading progress: {e}")
            return {"error": str(e)}

    def mark_essay_completed(self, data):
        """Mark essay as completed."""
        try:
            essay_id = data.get('essay_id')
            session_id = data.get('session_id')

            if not essay_id or not session_id:
                return {"error": "Missing required fields"}

            # Get existing record
            response = supabase_client.table(f"{SCHEMA}.essay_metrics") \
                .select("*") \
                .eq("essay_id", essay_id) \
                .eq("session_id", session_id) \
                .execute()

            if response.data:
                record = response.data[0]
                if not record["completed"]:
                    supabase_client.table(f"{SCHEMA}.essay_metrics") \
                        .update({"completed": True, "max_progress": 100}) \
                        .eq("id", record["id"]) \
                        .execute()

            return {"success": True}
        except Exception as e:
            print(f"Error marking essay as completed: {e}")
            return {"error": str(e)}

    def save_reading_metrics(self, data):
        """Save reading metrics."""
        try:
            essay_id = data.get('essay_id')
            reading_time = data.get('reading_time')
            session_id = data.get('session_id')

            if not essay_id or reading_time is None or not session_id:
                return {"error": "Missing required fields"}

            # Get existing record
            response = supabase_client.table(f"{SCHEMA}.essay_metrics") \
                .select("*") \
                .eq("essay_id", essay_id) \
                .eq("session_id", session_id) \
                .execute()

            if response.data:
                record = response.data[0]
                supabase_client.table(f"{SCHEMA}.essay_metrics") \
                    .update({"total_reading_time": record["total_reading_time"] + reading_time}) \
                    .eq("id", record["id"]) \
                    .execute()

            return {"success": True}
        except Exception as e:
            print(f"Error saving reading metrics: {e}")
            return {"error": str(e)}

def run_server(port=8080):
    """Run the API server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"Starting metrics API server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
