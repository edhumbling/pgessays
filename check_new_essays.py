#!/usr/bin/env python3
"""
Simple script to check if there are any new Paul Graham essays.
This script will:
1. Load our existing essays from essays.csv
2. Get the URL of the most recent essay from Paul Graham's website
3. Check if that URL is already in our database
4. Only if it's not, then we process it
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Constants
PG_ARTICLES_URL = "http://www.paulgraham.com/articles.html"
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def get_existing_essay_urls():
    """Get the list of URLs for existing essays from the essays.csv file."""
    existing_urls = set()
    
    if os.path.exists(ESSAYS_CSV):
        try:
            df = pd.read_csv(ESSAYS_CSV)
            existing_urls = set(df['URL'].tolist())
            print(f"Found {len(existing_urls)} existing essays in {ESSAYS_CSV}")
        except Exception as e:
            print(f"Error reading {ESSAYS_CSV}: {e}")
    
    return existing_urls

def get_latest_essay_url():
    """Get the URL of the most recent essay from Paul Graham's website."""
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(PG_ARTICLES_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links in the page
        links = soup.find_all('a')
        
        # Paul Graham's essays are listed with newest first
        for link in links:
            href = link.get('href')
            title = link.get_text().strip()
            
            # Skip empty links or non-essay links
            if not href or not title or href.startswith('#') or href.startswith('mailto:'):
                continue
                
            # Convert relative URLs to absolute
            url = urljoin(PG_ARTICLES_URL, href)
            
            # Only include links to paulgraham.com essays
            if 'paulgraham.com' in url and title:
                return url, title
        
        return None, None
    
    except Exception as e:
        print(f"Error fetching latest essay: {e}")
        return None, None

def main():
    """Main function to check for new essays."""
    print("Checking for new Paul Graham essays...")
    
    # Get existing essay URLs
    existing_urls = get_existing_essay_urls()
    
    # Get the URL of the most recent essay
    latest_url, latest_title = get_latest_essay_url()
    
    if not latest_url:
        print("Error: Could not fetch the latest essay from Paul Graham's website")
        return
    
    print(f"Latest essay: {latest_title} ({latest_url})")
    
    # Check if the latest essay is already in our database
    if latest_url in existing_urls:
        print("The latest essay is already in our database")
        print("No new essays to add")
    else:
        print("Found a new essay that is not in our database!")
        print(f"Title: {latest_title}")
        print(f"URL: {latest_url}")
        print("You can run the full update script to add this and any other new essays")

if __name__ == "__main__":
    main()
