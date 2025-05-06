#!/usr/bin/env python3
"""
Script to run the API server for essay metrics.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from api.metrics import run_server

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to run the API server."""
    parser = argparse.ArgumentParser(description='Run the API server for essay metrics.')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the server on')
    parser.add_argument('--supabase-key', type=str, help='Supabase service key')

    args = parser.parse_args()

    # Set environment variables
    if args.supabase_key:
        os.environ['SUPABASE_SERVICE_KEY'] = args.supabase_key

    # Check if the service key is set
    if not os.environ.get('SUPABASE_SERVICE_KEY'):
        print("Warning: SUPABASE_SERVICE_KEY environment variable is not set.")
        print("The API server will not be able to connect to Supabase.")
        print("Set it using --supabase-key or by setting the environment variable.")

    # Run the server
    run_server(args.port)

if __name__ == "__main__":
    main()
